from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0046_alter_comment_options_alter_product_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/product_images'),
        ),
    ]
