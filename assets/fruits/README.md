# Плоди для фону головного меню

Сюди кладуть картинки плодів користувача. Головне меню показує їх усередині кола для вибраної зони: по одній на кожен горщик.

Поки тут немає жодного `.png`, коло порожнє і меню навіть не відкриває зону.

Назви файлів:

- `{species_id}_{stage}.png` — плід на певному етапі, наприклад `cucumber_ripe.png`, `tomato_fruiting.png`.
- `{species_id}.png` — запасна картинка для будь-якого етапу, наприклад `cucumber.png`.

`species_id` — як у `app/knowledge/data/species.json` (`cucumber`, `tomato`, `strawberry`).
`stage` — `sprout`, `growing`, `flowering`, `fruiting`, `ripe`, `harvested`.

PNG з прозорим фоном, квадрат, бажано 256×256. Моделі `.glb` з `3d-models/` Flet не малює: з них треба зняти PNG.
