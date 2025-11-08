from django.urls import path
from .views import decompose, score, reward, level_story, narrative

urlpatterns = [
    path("decompose", decompose, name="ai_decompose"),
    path("score", score, name="ai_score"),
    path("reward", reward, name="ai_reward"),
    path("level-story", level_story, name="ai_level_story"),
    path("narrative", narrative, name="ai_narrative"),
]


