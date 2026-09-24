# Optional backfill for demo slugs when DB existed before cover_image.

from django.db import migrations


def backfill_images(apps, schema_editor):
    Hospital = apps.get_model("hospitals", "Hospital")
    mapping = {
        "aiims-patna": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1200&q=80",
        "pmch-patna": "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=1200&q=80",
        "igims-patna": "https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=1200&q=80",
        "paras-hospital": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200&q=80",
        "ruban-hospital": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=1200&q=80",
        "ford-hospital": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=1200&q=80",
        "apollo-spectra": "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=1200&q=80",
        "nmch-patna": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&q=80",
        "kurji-hospital": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=1200&q=80",
        "apex-hospital": "https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=1200&q=80",
    }
    for slug, url in mapping.items():
        Hospital.objects.filter(slug=slug, cover_image="").update(cover_image=url)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("hospitals", "0002_add_hospital_cover_image"),
    ]

    operations = [
        migrations.RunPython(backfill_images, noop_reverse),
    ]
