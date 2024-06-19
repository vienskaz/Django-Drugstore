# Generated by Django 4.2.4 on 2024-06-11 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_item_conflict_item_dosage'),
    ]

    operations = [
        migrations.CreateModel(
            name='DrugConflict',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drug1', models.CharField(max_length=500)),
                ('drug2', models.CharField(max_length=500)),
            ],
            options={
                'unique_together': {('drug1', 'drug2')},
            },
        ),
        migrations.RemoveField(
            model_name='item',
            name='conflict',
        ),
        migrations.CreateModel(
            name='DrugConflictItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conflict', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conflict_items', to='shop.drugconflict')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_conflicts', to='shop.item')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='conflicts',
            field=models.ManyToManyField(related_name='conflicted_by', through='shop.DrugConflictItem', to='shop.item'),
        ),
    ]