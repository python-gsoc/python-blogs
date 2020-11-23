'use strict';

var helpers = require('djangocms-casper-helpers');
var globals = helpers.settings;
var casperjs = require('casper');
var cms = helpers(casperjs);
var xPath = casperjs.selectXPath;

casper.test.setUp(function (done) {
    casper.start()
        .then(cms.login())
        .run(done);
});

casper.test.tearDown(function (done) {
    casper.start()
        .then(cms.logout())
        .run(done);
});

casper.test.begin('Creation of a new group', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            test.assertVisible('#content', 'Admin loaded');
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn_People',
                    row: 'Groups',
                    link: 'Add'
                }))
            );
        })
        .waitForUrl(/add/)
        .waitUntilVisible('#group_form')
        .then(function () {
            test.assertVisible('#group_form', 'Group creation form has been loaded');

            this.fill('#group_form', {
                name: 'Test group'
            }, true);
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Group "Test group" was added successfully.',
                'New group has been created'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Creation of a new people entry', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn_People',
                    row: 'People',
                    link: 'Add'
                }))
            );
        })
        .waitForUrl(/add/)
        .waitUntilVisible('#person_form')
        .then(function () {
            test.assertVisible('#person_form', 'People creation form has been loaded');

            this.fill('#person_form', {
                name: 'Test person'
            }, true);
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Person "Test person" was added successfully.',
                'New person has been created'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Adding a new people block to the page', function (test) {
    casper
        .start()
        .then(cms.addPage({ title: 'People' }))
        .then(cms.addPlugin({
            type: 'PeoplePlugin'
        }))
        .thenOpen(globals.editUrl, function () {
            test.assertTitleMatch(/People/, 'The People page has been created');
        })
        .then(cms.publishPage({ page: 'People' }))
        .thenOpen(globals.editUrl, function () {
            test.assertSelectorHasText(
                '.cms-plugin h2',
                'Test person',
                'The newly created "Test person" is displayed on the "People" page'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Deletion of a group', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn_People',
                    row: 'Groups',
                    link: 'Change'
                }))
            );
        })
        .waitForUrl(/group/)
        .waitUntilVisible('#result_list', function () {
            test.assertElementCount(
                '#result_list tbody tr',
                1,
                'The group is available'
            );

            this.clickLabel('Test group', 'a');
        })
        .waitUntilVisible('.deletelink', function () {
            this.click('.deletelink');
        })
        .waitForUrl(/delete/, function () {
            this.click('input[value="Yes, I\'m sure"]');
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Group "Test group" was deleted successfully.',
                'The group has been deleted'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Deletion of a people entry', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn_People',
                    row: 'People',
                    link: 'Change'
                }))
            );
        })
        .waitForUrl(/person/)
        .waitUntilVisible('#result_list', function () {
            test.assertElementCount(
                '#result_list tbody tr',
                1,
                'The people entry is available'
            );

            this.clickLabel('Test person', 'a');
        })
        .waitUntilVisible('.deletelink', function () {
            this.click('.deletelink');
        })
        .waitForUrl(/delete/, function () {
            this.click('input[value="Yes, I\'m sure"]');
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Person "Test person" was deleted successfully.',
                'The person has been deleted'
            );
        })
        .run(function () {
            test.done();
        });
});
