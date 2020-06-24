/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, expect, beforeEach, afterEach, fixture */

// #############################################################################
// UNIT TEST
describe('cl.people.js:', function () {
    beforeEach(function () {
        fixture.setBase('frontend/fixtures');
        this.markup = fixture.load('people.html');
        this.preventEvent = { preventDefault: function () {} };
    });

    afterEach(function () {
        fixture.cleanup();
    });

    it('runs dummy test', function () {
        expect('dummy test').toEqual('dummy test');
    });

});
