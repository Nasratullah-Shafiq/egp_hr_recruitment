/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

// Extend the existing hrRecruitment widget
publicWidget.registry.hrRecruitment = publicWidget.Widget.extend({
    // Keep the original selector
    selector: '#hr_recruitment_form',

    // Extend events (not override)
    events: function() {
        return _.extend({}, this._super(), {
            'focusout #tazkira_number': '_onFocusOutTazkira',
        });
    },

    init: function() {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
        this._isTazkiraValid = true;
    },

    // Add new method for Tazkira validation
    async _onFocusOutTazkira(ev) {
        const tazkira = $(ev.currentTarget).val();
        const $tazkiraInput = $(ev.currentTarget);
        let $tazkiraMessage = $('#tazkira-message');

        // Create message container if it doesn't exist
        if (!$tazkiraMessage.length) {
            $tazkiraInput.after('<div id="tazkira-message" class="alert alert-warning mt-2" style="display: none;"></div>');
            $tazkiraMessage = $('#tazkira-message');
        }

        if (!tazkira) {
            $tazkiraInput.removeClass('border-warning');
            $tazkiraMessage.hide();
            this._isTazkiraValid = true;
            return;
        }

        // Validate Tazkira format (adjust regex as per your requirement)
        // Example: Alphanumeric, 5-20 characters
        const tazkira_regex = /^[A-Za-z0-9]{5,20}$/;
        if (!tazkira_regex.test(tazkira)) {
            $tazkiraInput.addClass('border-warning');
            $tazkiraMessage.text(_t("Please enter a valid Tazkira Number (5-20 alphanumeric characters)")).show();
            this._isTazkiraValid = false;
            return;
        }

        // Check for duplicates via RPC
        try {
            const data = await this.rpc('/egp_hr_recruitment/check_tazkira', {
                tazkira_number: tazkira,
            });

            if (data.exists) {
                $tazkiraInput.addClass('border-warning');
                $tazkiraMessage.text(_t(data.message)).show();
                this._isTazkiraValid = false;
            } else {
                $tazkiraInput.removeClass('border-warning');
                $tazkiraMessage.hide();
                this._isTazkiraValid = true;
            }
        } catch (error) {
            console.error("Error checking Tazkira:", error);
            this._isTazkiraValid = true;
        }
    },

    // Override the apply button click to include Tazkira validation
    _onClickApplyButton: function(ev) {
        // Call original validation if exists
        if (this._super) {
            this._super(ev);
        }

        // Add Tazkira validation
        const $tazkira = $('#tazkira_number');
        const tazkira = $tazkira.val();

        if (tazkira && !this._isTazkiraValid) {
            ev.preventDefault();
            ev.stopPropagation();
            $('#tazkira-message').show();
            return false;
        }

        // Original LinkedIn and Resume validation
        const $linkedin_profile = $('#recruitment4');
        const $resume = $('#recruitment6');

        const is_linkedin_empty = !$linkedin_profile.length || $linkedin_profile.val().trim() === '';
        const is_resume_empty = !$resume.length || !$resume[0].files.length;

        if (is_linkedin_empty && is_resume_empty) {
            $linkedin_profile.attr('required', true);
            $resume.attr('required', true);
        } else {
            $linkedin_profile.attr('required', false);
            $resume.attr('required', false);
        }
    },
});