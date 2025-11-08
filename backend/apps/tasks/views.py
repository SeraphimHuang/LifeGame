import random
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Task, Subtask, LevelStory
from .serializers import TaskListSerializer, TaskDetailSerializer, SubtaskSerializer, LevelStorySerializer
from apps.inventory.models import Item
from apps.inventory.serializers import ItemSerializer
from apps.config.models import DropConfig
from apps.accounts.models import UserProfile
from apps.config.models import AttributeMapping
from apps.ai.views import infer_attribute_weights
from apps.ai.services import llm_json


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Task):
            return obj.created_by_id == request.user.id
        if isinstance(obj, Subtask):
            return obj.task.created_by_id == request.user.id
        return False


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = "id"
    serializer_class = TaskDetailSerializer

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        return TaskDetailSerializer

    def perform_create(self, serializer):
        # 单任务流程B：存在进行中任务时禁止创建新任务
        if Task.objects.filter(created_by=self.request.user, status=Task.Status.DOING).exists():
            raise PermissionError("已有进行中任务，无法创建新任务")
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, id=None):
        task = self.get_object()
        # 已有其他进行中任务则阻止
        other_doing = Task.objects.filter(
            created_by=request.user, status=Task.Status.DOING
        ).exclude(id=task.id)
        if other_doing.exists():
            return Response({"detail": "已有进行中任务"}, status=status.HTTP_409_CONFLICT)
        if task.status == Task.Status.DONE:
            return Response({"detail": "任务已完成"}, status=status.HTTP_400_BAD_REQUEST)
        task.status = Task.Status.DOING
        from django.utils import timezone
        task.started_at = timezone.now()
        task.save()
        return Response(TaskDetailSerializer(task).data)

    @action(detail=True, methods=["post"])
    def subtasks(self, request, id=None):
        # Add a subtask
        task = self.get_object()
        title = request.data.get("title", "").strip()
        estimate_seconds = request.data.get("estimate_seconds", None)
        if not title:
            return Response({"detail": "title required"}, status=status.HTTP_400_BAD_REQUEST)
        position = (task.subtasks.aggregate(max_pos=models.Max("position"))["max_pos"] or 0) + 1  # type: ignore
        st = Subtask.objects.create(task=task, title=title, estimate_seconds=estimate_seconds, position=position)
        return Response(SubtaskSerializer(st).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="subtasks/reorder")
    def subtasks_reorder(self, request, id=None):
        task = self.get_object()
        items = request.data if isinstance(request.data, list) else request.data.get("items", [])
        if not isinstance(items, list):
            return Response({"detail": "invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            for row in items:
                sid = row.get("subtaskId")
                pos = row.get("position")
                if sid is None or pos is None:
                    continue
                Subtask.objects.filter(task=task, id=sid).update(position=pos)
        return Response({"detail": "ok"})

    @action(detail=True, methods=["post"], url_path=r"subtasks/(?P<sid>[^/]+)/toggle")
    def subtask_toggle(self, request, id=None, sid=None):
        task = self.get_object()
        st = get_object_or_404(Subtask, task=task, id=sid)
        st.status = Subtask.Status.DONE if st.status == Subtask.Status.TODO else Subtask.Status.TODO
        st.save()
        return Response(SubtaskSerializer(st).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, id=None):
        task = self.get_object()
        if task.status == Task.Status.DONE:
            return Response({"detail": "任务已完成"}, status=status.HTTP_400_BAD_REQUEST)
        # 校验所有子任务完成（若无子任务则允许直接完成）
        if task.subtasks.exists() and task.subtasks.filter(status=Subtask.Status.TODO).exists():
            return Response({"detail": "尚有未完成的子任务"}, status=status.HTTP_400_BAD_REQUEST)
        final_score = task.final_score
        level_ups = []
        dropped_item = None
        with transaction.atomic():
            # 标记完成
            task.status = Task.Status.DONE
            from django.utils import timezone
            task.finished_at = timezone.now()
            task.save()
            # XP & Level
            profile = UserProfile.objects.select_for_update().get(user=request.user)
            profile.xp += final_score
            # 属性加点（方案B，无全局系数；优先用任务权重，否则 AI 推断；向上取整）
            hint = task.attribute_weights or infer_attribute_weights(task.title)
            def clamp01(x): 
                try:
                    v = float(x)
                    return max(0.0, min(1.0, v))
                except Exception:
                    return 0.0
            def gain_of(key: str) -> float:
                return round(final_score * clamp01(hint.get(key, 0)) / 10.0, 1)
            gains = {
                "learning": gain_of("learning"),
                "stamina": gain_of("stamina"),
                "charisma": gain_of("charisma"),
                "craft": gain_of("craft"),
                "inspiration": gain_of("inspiration"),
            }
            for k, v in gains.items():
                cur = profile.attributes.get(k, 0) or 0
                profile.attributes[k] = round(float(cur) + float(v), 1)
            # 升级循环
            while profile.xp >= 100:
                profile.xp -= 100
                profile.level += 1
                # 尝试用LLM生成故事，失败回退
                schema = '{"title":"等级X的边界","content":"……"}'
                prompt = (
                    "用中性第三人称写一段奇幻冒险短文，称呼固定为“勇者{display_name}”。"
                    f"长度约{200 + profile.xp * 3}字；允许出现在荒野与城市间往来。近期任务：[{task.title}]"
                ).replace("{display_name}", request.user.username)
                story = llm_json(prompt, schema) or self._generate_level_story(request.user.username, profile.level, task.title, final_score)
                ls = LevelStory.objects.create(user=request.user, level=profile.level, title=story["title"], content=story["content"])
                level_ups.append(LevelStorySerializer(ls).data)
            profile.save()
            # 掉落判定
            band_prob = self._get_drop_prob(final_score)
            if random.random() < band_prob:
                # LLM生成奖励物品，失败回退
                schema = '{"name":"回声指环","description":"……"}'
                prompt = (
                    "生成一件奇幻风但不带数值的物品，用于任务奖励。返回JSON包含 name 与 description。"
                    f"主导属性：{max(gains, key=gains.get)}；任务摘要：{task.title}。"
                )
                data = llm_json(prompt, schema)
                name = (data or {}).get("name") or self._generate_item_name(task)
                desc = (data or {}).get("description") or self._generate_item_description(task)
                item = Item.objects.create(name=name, description=desc, source_task=task)
                dropped_item = ItemSerializer(item).data
        new_profile = {
            "level": profile.level,
            "xp": profile.xp,
            "attributes": profile.attributes,
        }
        return Response(
            {"final_score": final_score, "dropped_item": dropped_item, "level_ups": level_ups, "new_profile": new_profile}
        )

    def _get_drop_prob(self, score: int) -> float:
        dc = DropConfig.objects.first()
        if not dc:
            # 默认与分数无关的基础概率
            return 0.2
        for band in dc.bands:
            if band["min"] <= score <= band["max"]:
                return float(band["prob"])
        return 0.2

    def _generate_level_story(self, display_name: str, level: int, last_task_title: str, last_score: int):
        base = 200 + last_score * 3
        content = (
            f"在新的旅程里，勇者{display_name}整备行囊，从营地出发，踏入城与荒野之间的缝隙。"
            f"近期的试炼“{last_task_title}”让心志更稳，力量更凝。夜色如墨，风声如歌，"
            f"每一步都在旧地图之外落下新的注脚。此后，{display_name}将以更从容的姿态面对陌生的关隘。"
        )
        # 仅占位：实际长度不强制达标
        return {"title": f"等级 {level} 的边界", "content": content}

    def _generate_item_name(self, task: Task) -> str:
        # 简单按标题生成一个偏战斗风名称
        keywords = ["剑", "枪", "刃", "纹章", "指环", "护腕", "厨刀", "铁锤"]
        suffix = random.choice(keywords)
        return f"{task.title[:8]}之{suffix}"

    def _generate_item_description(self, task: Task) -> str:
        return (
            "完成此役后，它在夜里泛出一线微光。挥动时，像是把犹豫劈成了两半，"
            "提醒旅人继续前行。"
        )

