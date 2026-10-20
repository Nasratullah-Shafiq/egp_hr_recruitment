/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.PortalLocationSelector = publicWidget.Widget.extend({
    selector: '.s_website_form_field',

    events: {
        'change #country_id': '_onCountryChange',
        'change #current_country_id': '_onCountryChange',
        'change #province_id': '_onProvinceChange',
        'change #current_province_id': '_onProvinceChange',
    },

    /**
     * Auto trigger when page loads
     */
    start: function () {
    this._super.apply(this, arguments);

    const $country = $('#country_id');

    if ($country.val()) {

        // Permanent address provinces
        this._loadProvinces($country.val());

        // Current address provinces
        this._loadCurrentProvinces($country.val());
    }
},

    /**
     * Load provinces for permanent address
     */
    _loadProvinces: function (countryId) {
        const $provinceSelect = $('#province_id');
        const $districtSelect = $('#district_id');

        $provinceSelect.html('<option value="">Select Province...</option>').prop('disabled', true);
        $districtSelect.html('<option value="">Select District...</option>').prop('disabled', true);

        if (countryId) {
            jsonrpc('/get_provinces', {
                country_id: countryId
            }).then(function (provinces) {

                if (provinces.length > 0) {
                    $provinceSelect.prop('disabled', false);

                    provinces.forEach(function (province) {
                        $provinceSelect.append(
                            new Option(province.name, province.id)
                        );
                    });
                }
            });
        }
    },

    /**
     * Load provinces for current address
     */
    _loadCurrentProvinces: function (countryId) {
        const $currentProvinceSelect = $('#current_province_id');
        const $currentDistrictSelect = $('#current_district_id');

        $currentProvinceSelect.html('<option value="">Select Province...</option>').prop('disabled', true);

        $currentDistrictSelect.html('<option value="">Select District...</option>').prop('disabled', true);

        if (countryId) {
            jsonrpc('/get_provinces', {
                country_id: countryId
            }).then(function (provinces) {

                if (provinces.length > 0) {
                    $currentProvinceSelect.prop('disabled', false);

                    provinces.forEach(function (province) {
                        $currentProvinceSelect.append(
                            new Option(province.name, province.id)
                        );
                    });
                }
            });
        }
    },

    /**
     * Country changed manually
     */
    _onCountryChange: function (ev) {
        const countryId = $(ev.target).val();
        const fieldId = ev.target.id;

        if (fieldId === 'country_id') {

    // Permanent Address
    this._loadProvinces(countryId);

    // Current Address
    this._loadCurrentProvinces(countryId);
        }
    },

    /**
     * Province changed
     */
    _onProvinceChange: function (ev) {
        const provinceId = $(ev.target).val();
        const fieldId = ev.target.id;

        let $districtSelect;

        if (fieldId === 'province_id') {
            $districtSelect = $('#district_id');
        } else if (fieldId === 'current_province_id') {
            $districtSelect = $('#current_district_id');
        }

        $districtSelect.html('<option value="">Select District...</option>')
            .prop('disabled', true);

        if (provinceId) {
            jsonrpc('/get_districts', {
                province_id: provinceId
            }).then(function (districts) {

                if (districts.length > 0) {
                    $districtSelect.prop('disabled', false);

                    districts.forEach(function (district) {
                        $districtSelect.append(
                            new Option(district.name, district.id)
                        );
                    });
                }
            });
        }
    },
});