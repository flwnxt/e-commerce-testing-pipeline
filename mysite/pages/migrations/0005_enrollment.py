from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_alter_pricingpage_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=8)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='enrollments',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='enrollments',
                    to='pages.coursedetailpage',
                )),
            ],
            options={
                'ordering': ['-enrolled_at'],
                'unique_together': {('user', 'course')},
                'indexes': [
                    models.Index(fields=['user'], name='enrollment_user_idx'),
                    models.Index(fields=['course'], name='enrollment_course_idx'),
                ],
            },
        ),
    ]
