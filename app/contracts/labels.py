"""Усі видимі написи. Екрани беруть рядки звідси, а не пишуть свої."""

from app.contracts.constants import GROUP_MIN_POTS
from app.contracts.models import (
    AlertSeverity,
    CareAction,
    Category,
    GrowthStage,
    Mood,
    SoilType,
    ZoneKind,
)

APP_NAME = "HappyGarden"
SUBTITLE = "Твоя грядка в кишені"

BTN_ENTER = "До грядки"
BTN_ZONES = "Мої зони"
BTN_FRIENDS = "Друзі"
BTN_SETTINGS = "Налаштування"
BTN_STATUS = "Стан"
BTN_BACK = "Назад"
BTN_PLANT = "Посадити"
BTN_WATER = "Полити"
BTN_FERTILIZE = "Удобрити"
BTN_HARVEST = "Зібрати"
BTN_GROUP = "Згрупувати врожай"
BTN_LOOKUP = "Підібрати довідку"
BTN_CREATE_ZONE = "Створити зону"
BTN_DELETE_POT = "Видалити"
BTN_CHANGE_POT = "Змінити"
BTN_POT_INFO = "Відомості"
BTN_ADD_FRIEND = "Додати друга"
BTN_DAY_PLUS = "+1 день"
BTN_DAY_MINUS = "−1 день"
BTN_ZOOM_IN = "+"
BTN_ZOOM_OUT = "−"
BTN_SIGN_IN = "Увійти"
BTN_SIGN_UP = "Створити акаунт"
BTN_GOOGLE = "Продовжити з Google"
BTN_HAVE_ACCOUNT = "Вже маєте акаунт? Увійти"
BTN_NO_ACCOUNT = "Немає акаунту? Зареєструватися"
LBL_EMAIL = "Email"
LBL_PASSWORD = "Пароль"
LBL_PASSWORD_CONFIRM = "Повторіть пароль"
LBL_PRIVACY = "Privacy Policy"
LBL_TERMS = "Terms"
LBL_SUPPORT = "Support"
LBL_MARKETING = "Marketing"
AUTH_SUBTITLE_SIGN_IN = "Увійди, щоб зберегти сад"
AUTH_SUBTITLE_SIGN_UP = "Створи акаунт для саду"
ONBOARDING_TITLE = "Створи першу зону"
ONBOARDING_SUBTITLE = "Акаунт уже є — тепер назви грядку"
BTN_LOGOUT = "Вийти з акаунта"
BTN_DELETE_ACCOUNT = "Видалити акаунт"
BTN_CONFIRM_DELETE_ACCOUNT = "Так, видалити"
BTN_CANCEL = "Скасувати"
DELETE_ACCOUNT_HINT = "Акаунт зникне назавжди. Сад на цьому пристрої також зітреться."
LBL_LEGAL = "Документи"

HINT_SWIPE = "Свайпни вгору"
EMPTY_ZONES = "Ще немає жодної зони"
EMPTY_POTS = "Посади першу рослину"
GROUP_HINT = f"Група збирається від {GROUP_MIN_POTS} горщиків одного виду"
UNVERIFIED_NOTE = "Числа чорнові: джерело ще не підтверджене."
OFFLINE_WEATHER = "Погоду не вдалося отримати. Грядка працює далі без неї."
NO_DATA = "Немає даних"
EMPTY_TIMELINE = "Календар етапів з'явиться разом із довідкою"

LBL_SPECIES = "Культура"
LBL_VARIETY = "Сорт"
LBL_SOIL = "Ґрунт"
LBL_TERRITORY = "Місцевість"
LBL_ZONE_KIND = "Де росте"
LBL_ZONE_NAME = "Назва зони"
LBL_NICKNAME = "Твій нік"
LBL_FRIEND = "Нік друга"
LBL_POINTS = "Очки"
LBL_SOURCES = "Джерела"
LBL_SUMMARY = "Довідка"
LBL_TIPS = "Поради"
LBL_TIMELINE = "Етапи дозрівання"
LBL_ALERTS = "Погода"
LBL_REMINDERS = "Нагадування"
LBL_DAY = "День симуляції"
LBL_MOISTURE = "Волога"
LBL_SOIL_QUALITY = "Якість землі"
LBL_FERTILITY = "Родючість"
LBL_HEALTH = "Здоров'я"
LBL_STAGE = "Етап"
LBL_MOOD = "Настрій"

STAGE_LABELS: dict[GrowthStage, str] = {
    GrowthStage.SPROUT: "Паростки",
    GrowthStage.GROWING: "Ріст",
    GrowthStage.FLOWERING: "Цвітіння",
    GrowthStage.FRUITING: "Плоди",
    GrowthStage.RIPE: "Стиглі",
    GrowthStage.HARVESTED: "Зібрано",
}

MOOD_LABELS: dict[Mood, str] = {
    Mood.HAPPY: "Радіє",
    Mood.OK: "Нормально",
    Mood.THIRSTY: "Хоче пити",
    Mood.SAD: "Сумно",
}

ZONE_LABELS: dict[ZoneKind, str] = {
    ZoneKind.GREENHOUSE: "Теплиця",
    ZoneKind.GARDEN: "Город",
    ZoneKind.FARM: "Фазенда",
}

SOIL_LABELS: dict[SoilType, str] = {
    SoilType.CHERNOZEM: "Чорнозем",
    SoilType.LOAM: "Суглинок",
    SoilType.SAND: "Пісок",
    SoilType.PEAT: "Торф",
    SoilType.CLAY: "Глина",
}

CATEGORY_LABELS: dict[Category, str] = {
    Category.VEGETABLE: "Овоч",
    Category.FRUIT: "Фрукт",
}

ACTION_LABELS: dict[CareAction, str] = {
    CareAction.PLANT: "Посадка",
    CareAction.WATER: BTN_WATER,
    CareAction.FERTILIZE: BTN_FERTILIZE,
    CareAction.HARVEST: BTN_HARVEST,
}

SEVERITY_LABELS: dict[AlertSeverity, str] = {
    AlertSeverity.INFO: "Нотатка",
    AlertSeverity.WARNING: "Увага",
    AlertSeverity.DANGER: "Небезпека",
}


def as_percent(value: float) -> int:
    if value < 0:
        value = 0.0
    if value > 1:
        value = 1.0
    return int(round(value * 100))
