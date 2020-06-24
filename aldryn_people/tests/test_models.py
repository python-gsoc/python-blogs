# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TransactionTestCase
from django.utils.encoding import force_text
from django.utils.translation import override

from . import BasePeopleTest, DefaultApphookMixin
from ..models import Group, Person


class TestBasicPeopleModels(DefaultApphookMixin, BasePeopleTest):

    def test_create_person(self):
        """We can create a person with a name."""
        name = 'Tom Test'
        person = Person.objects.create(name=name)
        person.refresh_from_db()
        self.assertEqual(person.name, name)

    def test_delete_person(self):
        """We can delete a person."""
        name = 'Person Delete'
        person = Person.objects.create(name=name)
        Person.objects.get(pk=person.pk).delete()
        self.assertFalse(Person.objects.filter(pk=person.pk))

    def test_str(self):
        name = 'Person Str'
        person = Person.objects.create(name=name)
        self.assertEqual(force_text(person), name)

    def test_absolute_url(self):
        slug = 'person-slug'
        person = Person.objects.create(slug=slug)
        # This isn't a translation test, per se, but let's make sure that we
        # have a predictable language prefix, regardless of the tester's locale.
        with override('en'):
            app_hook_url = self.app_hook_page.get_absolute_url()
            self.assertEqual(
                person.get_absolute_url(),
                '{0}{1}/'.format(app_hook_url, slug)
            )
            # Now test that it will work when there's no slug too.
            person.slug = ''
            self.assertEqual(
                person.get_absolute_url(),
                '{0}{1}/'.format(app_hook_url, person.pk),
            )

    def test_auto_slugify(self):
        name = 'Melchior Hoffman'
        slug = 'melchior-hoffman'
        person = Person.objects.create(name=name)
        person.save()
        self.assertEquals(person.slug, slug)

    def test_auto_slugify_same_name(self):
        name_1 = 'Melchior Hoffman'
        slug_1 = 'melchior-hoffman'
        person_1 = Person.objects.create(name=name_1)
        person_1.save()

        name_2 = 'Melchior Hoffman'
        slug_2 = 'melchior-hoffman-1'
        person_2 = Person.objects.create(name=name_2)
        person_2.save()

        self.assertEquals(person_1.slug, slug_1)
        self.assertEquals(person_2.slug, slug_2)


class TestBasicGroupModel(TransactionTestCase):

    def test_create_group(self):
        """We can create a group with a name."""
        group = Group.objects.create(name='group_b')
        self.assertTrue(group.name, 'group_b')

    def test_delete_group(self):
        """We can delete a group."""
        name = 'Group Delete'
        Group.objects.create(name=name)
        group = Group.objects.translated(name=name)
        if group:
            group[0].delete()
        self.assertFalse(Group.objects.translated(name=name))

    def test_create_another_group(self):
        """we create a group."""
        name = 'Gruppe Neu'
        group = Group.objects.create(name=name)
        self.assertEqual(group.name, name)
        self.assertEqual(Group.objects.all()[0], group)

    def test_add_person_to_group(self):
        """We create a person and add her to the created group."""
        personname = 'Daniel'
        person = Person.objects.create(name=personname)
        name = 'Group One'
        group = Group.objects.create(name=name)
        person.groups.add(group)
        person.save()
        self.assertIn(person, group.people.all())


class TestPersonModelTranslation(BasePeopleTest):

    def test_person_translatable(self):
        person1 = self.reload(self.person1, 'en')
        self.assertEqual(
            person1.function,
            self.data['person1']['en']['function']
        )
        person1 = self.reload(self.person1, 'de')
        self.assertEqual(
            person1.safe_translation_getter('function'),
            self.data['person1']['de']['function']
        )

    def test_comment(self):
        person1 = self.reload(self.person1, 'en')
        self.assertEqual(
            person1.comment,
            self.data['person1']['en']['description']
        )
        person1 = self.reload(self.person1, 'de')
        self.assertEqual(
            person1.comment,
            self.data['person1']['de']['description']
        )

    def test_get_vcard(self):
        person1 = self.reload(self.person1, 'en')
        # Test with no group
        vcard_en = ('BEGIN:VCARD\r\n'
                    'VERSION:3.0\r\n'
                    'FN:person1\r\n'
                    'N:;person1;;;\r\n'
                    'TITLE:function1\r\n'
                    'END:VCARD\r\n')
        self.assertEqual(
            person1.get_vcard().decode('utf-8'),
            vcard_en
        )
        # Test with a group and other fields populated
        group1 = self.reload(self.group1, 'en')
        group1.address = '123 Main Street'
        group1.city = 'Anytown'
        group1.postal_code = '12345'
        group1.phone = '+1 (234) 567-8903'
        group1.fax = '+1 (234) 567-8904'
        group1.website = 'www.groupwebsite.com'
        group1.save()
        person1.groups.add(group1)
        person1.email = 'person@org.org'
        person1.phone = '+1 (234) 567-8900'
        person1.mobile = '+1 (234) 567-8901'
        person1.fax = '+1 (234) 567-8902'
        person1.website = 'www.website.com'
        person1.save()
        vcard_en = ('BEGIN:VCARD\r\n'
                    'VERSION:3.0\r\n'
                    'FN:person1\r\n'
                    'N:;person1;;;\r\n'
                    'EMAIL:person@org.org\r\n'
                    'TITLE:function1\r\n'
                    'TEL;TYPE=WORK:+1 (234) 567-8900\r\n'
                    'TEL;TYPE=CELL:+1 (234) 567-8901\r\n'
                    'TEL;TYPE=FAX:+1 (234) 567-8902\r\n'
                    'URL:www.website.com\r\n'
                    'ORG:group1\r\n'
                    'ADR;TYPE=WORK:;;123 Main Street;Anytown;;12345;\r\n'
                    'TEL;TYPE=WORK:+1 (234) 567-8903\r\n'
                    'TEL;TYPE=FAX:+1 (234) 567-8904\r\n'
                    'URL:www.groupwebsite.com\r\n'
                    'END:VCARD\r\n')
        self.assertEqual(
            person1.get_vcard().decode('utf-8'),
            vcard_en
        )
        # Ensure this works for other langs too
        person1 = self.reload(self.person1, 'de')
        vcard_de = ('BEGIN:VCARD\r\n'
                    'VERSION:3.0\r\n'
                    'FN:mensch1\r\n'
                    'N:;mensch1;;;\r\n'
                    'EMAIL:person@org.org\r\n'
                    'TITLE:Funktion1\r\n'
                    'TEL;TYPE=WORK:+1 (234) 567-8900\r\n'
                    'TEL;TYPE=CELL:+1 (234) 567-8901\r\n'
                    'TEL;TYPE=FAX:+1 (234) 567-8902\r\n'
                    'URL:www.website.com\r\n'
                    'ORG:Gruppe1\r\n'
                    'ADR;TYPE=WORK:;;123 Main Street;Anytown;;12345;\r\n'
                    'TEL;TYPE=WORK:+1 (234) 567-8903\r\n'
                    'TEL;TYPE=FAX:+1 (234) 567-8904\r\n'
                    'URL:www.groupwebsite.com\r\n'
                    'END:VCARD\r\n')
        with override('de'):
            self.assertEqual(
                person1.get_vcard().decode('utf-8'),
                vcard_de
            )


class TestGroupModelTranslation(BasePeopleTest):

    def test_group_translation(self):
        group1 = self.reload(self.group1, 'en')
        self.assertEqual(group1.name, self.data['group1']['en']['name'])
        group1 = self.reload(self.group1, 'de')
        self.assertEqual(group1.name, self.data['group1']['de']['name'])

    def test_company_name(self):
        group1 = self.reload(self.group1, 'en')
        self.assertEqual(
            group1.company_name,
            self.data['group1']['en']['name'],
        )
        group1 = self.reload(self.group1, 'de')
        self.assertEqual(
            group1.company_name,
            self.data['group1']['de']['name'],
        )

    def test_company_description(self):
        group1 = self.reload(self.group1, 'en')
        self.assertEqual(
            group1.company_description,
            self.data['group1']['en']['description'],
        )
        group1 = self.reload(self.group1, 'de')
        self.assertEqual(
            group1.company_description,
            self.data['group1']['de']['description'],
        )

    def test_str(self):
        group1 = self.reload(self.group1, 'en')
        self.assertEqual(
            force_text(group1),
            self.data['group1']['en']['name'],
        )
        group1 = self.reload(self.group1, 'de')
        self.assertEqual(
            force_text(group1),
            self.data['group1']['de']['name'],
        )
