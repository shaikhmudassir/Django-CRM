# Generated by Django 4.2.1 on 2024-02-16 14:36

import cms.blocks
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import modelcluster.fields
import wagtail.blocks
import wagtail.contrib.routable_page.models
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0025_alter_image_file_alter_rendition_file'),
        ('wagtailcore', '0083_workflowcontenttype'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogDetailPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('excerpt', wagtail.fields.RichTextField()),
                ('content', wagtail.fields.StreamField([('content_title', cms.blocks.BlogContentTitleBlock()), ('code', cms.blocks.BlogCodeBlock()), ('rich_text', cms.blocks.BlogRichTextBlock()), ('image', cms.blocks.BlogImageBlock())], null=True, use_json_field=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='BlogListPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtail.contrib.routable_page.models.RoutablePageMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('content', wagtail.fields.StreamField([('right_image_left_content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(required=False)), ('paragraph', wagtail.blocks.RichTextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('links', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('cta_url', wagtail.blocks.URLBlock(required=False)), ('cta_page', wagtail.blocks.PageChooserBlock(required=False)), ('cta_text', wagtail.blocks.CharBlock(default='Submit', max_length='50', required=False)), ('cta_image', wagtail.images.blocks.ImageChooserBlock(required=False))])))])), ('aboutapp', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(required=False)), ('paragraph', wagtail.blocks.RichTextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('sub_heading', wagtail.blocks.CharBlock(required=False)), ('sub_paragraph', wagtail.blocks.RichTextBlock(required=False)), ('cta_url', wagtail.blocks.URLBlock(required=False)), ('cta_page', wagtail.blocks.PageChooserBlock(required=False)), ('cta_text', wagtail.blocks.CharBlock(default='Submit', max_length='50', required=False)), ('links', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('text', wagtail.blocks.CharBlock(required=False))])))])), ('count', wagtail.blocks.StructBlock([('links', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('count', wagtail.blocks.CharBlock(default=85, required=False)), ('count_value', wagtail.blocks.CharBlock(required=False)), ('text', wagtail.blocks.CharBlock(required=False))])))])), ('appfeatures', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('cards', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('icon', wagtail.blocks.CharBlock(required=False)), ('card_heading', wagtail.blocks.CharBlock(required=False)), ('card_description', wagtail.blocks.CharBlock(required=False))])))])), ('pricing', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('cards', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('card_heading', wagtail.blocks.CharBlock(required=False)), ('card_price', wagtail.blocks.CharBlock(required=False)), ('card_description', wagtail.blocks.RichTextBlock(required=False)), ('cta_url', wagtail.blocks.URLBlock(required=False)), ('cta_page', wagtail.blocks.PageChooserBlock(required=False)), ('cta_text', wagtail.blocks.CharBlock(default='Choose Plan', max_length='50', required=False))])))])), ('carousel', wagtail.blocks.StructBlock([('sliders', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('description', wagtail.blocks.RichTextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('author', wagtail.blocks.CharBlock(required=False)), ('role', wagtail.blocks.CharBlock(required=False))])))])), ('leftimagerighttext', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(required=False)), ('paragraph', wagtail.blocks.RichTextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('links', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('cta_url', wagtail.blocks.URLBlock(required=False)), ('cta_page', wagtail.blocks.PageChooserBlock(required=False)), ('cta_text', wagtail.blocks.CharBlock(default='Submit', max_length='50', required=False)), ('cta_image', wagtail.images.blocks.ImageChooserBlock(required=False))])))])), ('homeblog', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('cards', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('blog_tag', wagtail.blocks.CharBlock(required=False)), ('blog_heading', wagtail.blocks.CharBlock(required=False)), ('cta_url', wagtail.blocks.URLBlock(required=False)), ('cta_page', wagtail.blocks.PageChooserBlock(required=False)), ('cta_text', wagtail.blocks.CharBlock(default='Read More', max_length='50', required=False))])))]))], null=True, use_json_field=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='link_title')),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, populate_from='title')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_title', models.CharField(blank=True, max_length=50, null=True, verbose_name='link_title')),
                ('link_url', models.CharField(blank=True, max_length=500)),
                ('open_in_new_tab', models.BooleanField(blank=True, default=False)),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='cms.menu')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubMenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('link_title', models.CharField(blank=True, max_length=50, null=True, verbose_name='link_title')),
                ('link_url', models.CharField(blank=True, max_length=500)),
                ('open_in_new_tab', models.BooleanField(blank=True, default=False)),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.page')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_menu_items', to='cms.menuitem')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github', models.URLField(blank=True, help_text='Github URL', null=True)),
                ('twitter', models.URLField(blank=True, help_text='Twitter URL', null=True)),
                ('linkedin', models.URLField(blank=True, help_text='linkedin URL', null=True)),
                ('sitemap', models.URLField(blank=True, help_text='Sitemap rss.xml', null=True)),
                ('logo', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
