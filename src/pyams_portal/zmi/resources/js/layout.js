/* global MyAMS */

'use strict';


if (window.$ === undefined) {
	window.$ = MyAMS.$;
}


/**
 * Current page location getter
 * @returns: current template page location
 */
const getLocation = () => {
    const config = $('#portal_config');
    return config.data('ams-location');
};


const portal = {

    i18n: {
        CANT_DELETE_ROW_WITH_PORTLETS: "A row containing portlets can't be removed!",
        CANT_DELETE_SLOT_WITH_PORTLETS: "A slot containing portlets can't be removed!",
        SWITCH_SLOT_VISIBILITY: "Show/hide slot"
    },

    /**
     * Global template management
     */
    template: {

        /** Initialize configuration */
        initConfig: () => {
            const config = $('#portal_config');
            if (config.data('ams-allowed-change')) {
                // Init sortables and resizables
                $('.rows', config).addClass('sortable');
                $('.slots', config).addClass('sortable');
                $('.slot', config).addClass('resizable');
                $('.portlets', config).addClass('sortable');
                MyAMS.registry.plugins.plugins.get('dragdrop').run(config).then(() => {
                    // Init rows toolbar drag and drop
                    $('.btn-row', '.btn-toolbar').draggable({
                        cursor: 'move',
                        helper: 'clone',
                        revert: 'invalid',
                        connectToSortable: '.rows'
                    });
                    $('.rows', config).droppable({
                        accept: '.btn-row',
                        drop: MyAMS.portal.template.dropRowButton
                    });
                    // Init slot toolbar drag and drop
                    $('.btn-slot', '.btn-toolbar').draggable({
                        cursor: 'move',
                        helper: 'clone',
                        revert: 'invalid',
                        connectToSortable: '.slots'
                    });
                    $('.slots', config).droppable({
                        accept: '.btn-slot',
                        drop: MyAMS.portal.template.dropSlotButton
                    });
                    // Init portlets toolbar drag and drop
                    $('.btn-portlet', '.btn-toolbar').draggable({
                        cursor: 'move',
                        helper: 'clone',
                        revert: 'invalid',
                        connectToSortable: '.portlets'
                    });
                    $('.portlets', config).droppable({
                        accept: '.btn-portlet',
                        hoverClass: 'portlets-hover',
                        activeClass: 'portlets-active',
                        drop: MyAMS.portal.template.dropPortletButton
                    });
                });
            }
        },

        /**
         * Display selector
         */
        selectDisplay: (evt) => {
            const device = $(evt.target).val();
            MyAMS.ajax.post(`${getLocation()}/get-slots-width.json`, {
                device: device
            }).then((result) => {
                const config = $('#portal_config');
                config.removeClassPrefix('container-');
                if (device) {
                    config.addClass(`container-${device}`);
                }
                $('.slot', config).removeClassPrefix('col-');
                for (const slotName in result) {
                    if (!result.hasOwnProperty(slotName)) {
                        continue;
                    }
                    const widths = result[slotName];
                    const slot = $(`.slot[data-ams-slot-name="${slotName}"]`, config);
                    if (device) {
                        slot.addClass(`col-${widths[device]}`);
                    } else {
                        for (const display in widths) {
                            if (!widths.hasOwnProperty(display)) {
                                continue;
                            }
                            slot.addClass(`col-${display}-${widths[display]}`);
                        }
                    }
                    slot.addClass(widths.css);
                }
            });
        },

        /**
         * Add new row
         */
        addRow: (evt) => {
            const src = evt.currentTarget;
            $(src).parents('.dropdown').dropdown('hide');
            MyAMS.ajax.post(`${getLocation()}/add-template-row.json`, {}).then((result) => {
                const rowId = result.row_id;
                const rows = $('.rows', '#portal_config');
                $('<div></div>')
                    .addClass('row context-menu')
                    .attr('data-ams-row-id', rowId)
                    .append($('<strong></strong>')
                        .addClass('row_id badge badge-danger pull-left')
                        .text(rowId+1))
                    .append($('<strong></strong>')
                        .addClass('row_id badge badge-danger pull-right')
                        .text(rowId+1))
                    .append($('<div></div>')
                        .addClass('slots')
                        .sortable({
                            placeholder: 'slot-highlight',
                            connectWith: '.slots',
                            over: MyAMS.portal.template.overSlots,
                            stop: MyAMS.portal.template.sortSlots
                        })
                        .droppable({
                            accept: '.btn-slot',
                            drop: MyAMS.portal.template.dropSlotButton
                        }))
                    .contextMenu({
                        menuSelector: '#rowMenu',
                        menuSelected: MyAMS.helpers.contextMenuHandler
                    })
                    .appendTo(rows);
                rows.sortable('refresh');
            });
        },

        /**
         * Row drop after dragging
         */
        dropRowButton: (event, ui) => {
            if (ui.draggable.hasClass('already-dropped')) {
                return;
            }
            console.debug(ui.draggable);
            ui.draggable.tooltip('hide');
            ui.draggable.addClass('already-dropped');
            MyAMS.ajax.post(`${getLocation()}/add-template-row.json`, {}).then((result) => {
                const rowId = result.row_id;
                const rows = $('.rows', '#portal_config');
                ui.draggable
                    .removeClassPrefix('btn')
                    .removeClassPrefix('ui-')
                    .removeClassPrefix('bg-')
                    .removeClass('hint')
                    .removeClass('already-dropped')
                    .removeAttr('data-original-title')
                    .removeAttr('style')
                    .addClass('row context-menu')
                    .attr('data-ams-row-id', rowId)
                    .empty()
                    .append($('<strong></strong>')
                        .addClass('row_id badge badge-danger pull-left')
                        .text(rowId+1))
                    .append($('<strong></strong>')
                        .addClass('row_id badge badge-danger pull-right')
                        .text(rowId+1))
                    .append($('<div></div>')
                        .addClass('slots')
                        .addClass('width-100')
                        .sortable({
                            placeholder: 'slot-highlight',
                            connectWith: '.slots',
                            over: MyAMS.portal.template.overSlots,
                            stop: MyAMS.portal.template.sortSlots
                        })
                        .droppable({
                            accept: '.btn-slot',
                            drop: MyAMS.portal.template.dropSlotButton
                        }))
                    .contextMenu({
                        menuSelector: '#rowMenu',
                        menuSelected: MyAMS.helpers.contextMenuHandler
                    });
                MyAMS.portal.template.sortRows();
                rows.sortable('refresh');
            });
        },

        /**
         * Row dragging over
         */
        overRows: (event, ui) => {
            $(ui.placeholder)
                .attr('class', $(ui.item).attr('class'))
                .removeClassPrefix('ui-')
                .addClass('row-highlight')
                .css('height', $(ui.item).outerHeight())
                .css('width', '100%');
        },

        /**
         * Rows sorting
         */
        sortRows: (event, ui) => {
            if (ui && ui.item.hasClass('already-dropped')) {
                return;
            }
            const config = $('#portal_config');
            const ids = $('.row', config).listattr('data-ams-row-id');
            MyAMS.ajax.post(`${getLocation()}/set-template-row-order.json`, {
                rows: JSON.stringify(ids)
            }).then((result) => {
                if (result.status === 'success') {
                    $('.row', config).each((idx, elt) => {
                        $(elt).attr('data-ams-row-id', idx);
                        $('.row_id', $(elt)).text(idx+1);
                    });
                }
            });
        },

        /**
         * Delete row
         */
        deleteRow: () => {
            return function(menuItem) {
                const menu = menuItem.parents('.dropdown-menu'),
                      row = menu.data('contextmenu-event-source'),
                      portlets = $('.portlet', row);
                MyAMS.require('alert').then(() => {
                    if (portlets.exists()) {
                        MyAMS.alert.messageBox({
                            status: 'error',
                            title: MyAMS.i18n.ERROR_OCCURED,
                            content: MyAMS.portal.i18n.CANT_DELETE_ROW_WITH_PORTLETS
                        });
                    } else {
                        MyAMS.alert.bigBox({
                            status: 'danger',
                            title: MyAMS.i18n.WARNING,
                            message: MyAMS.i18n.DELETE_WARNING,
                            icon: 'fas fa-bell'
                        }).then((result) => {
                            if (result === 'success') {
                                MyAMS.require('ajax').then(() => {
                                    MyAMS.ajax.post(`${getLocation()}/delete-template-row.json`, {
                                        row_id: row.data('ams-row-id')
                                    }).then((result) => {
                                        if (result.status === 'success') {
                                            row.remove();
                                            $('.row', '#portal_config').each((idx, elt) => {
                                                $(elt).removeData()
                                                    .attr('data-ams-row-id', idx);
                                                $('.row_id', elt).text(idx + 1);
                                            });
                                        }
                                    });
                                });
                            }
                        });
                    }
                });
            };
        },


        /**
         * Slots management
         */

        /**
         * Add new slot
         */
        addSlot: (evt) => {
            const src = evt.currentTarget;
            $(src).parents('.dropdown').dropdown('hide');
            MyAMS.require('modal').then(() => {
                MyAMS.modal.open(`${getLocation()}/add-template-slot.html`);
            });
        },

        /**
         * Slot add callback
         */
        addSlotCallback: (form, result) => {
            const
                slots = $('.slots', `.row[data-ams-row-id="${result.row_id}"]`),
                slotName = result.slot_name,
                device = $('#device_selector').val(),
                newSlot = $('<div></div>')
                    .addClass(`slot px-0 col col-12 col-${device}-12 resizable`)
                    .attr('data-ams-slot-name', slotName)
                    .append($('<div></div>')
                        .addClass('header px-1 d-flex align-items-center')
                        .append('<i class="action mr-1 fa fa-fw fa-minus-square pull-right padding-top-2" ' +
                                '   data-ams-click-handler="MyAMS.portal.template.switchSlot"></i>')
                        .append($('<span class="flex-grow-1"></span>')
                            .append(slotName)
                            .append('<i class="action ml-2 fa fa-fw fa-eye" ' +
                                    '   data-ams-click-handler="MyAMS.portal.template.switchSlotVisibility"></i>'))
                        .append('<i class="action fa fa-fw fa-edit float-right"' +
                                '   data-ams-click-handler="MyAMS.portal.template.editSlot"></i>')
                        .append('<i class="action fa fa-fw fa-trash float-right"' +
                                '   data-ams-click-handler="MyAMS.portal.template.deleteSlot"></i>'))
                    .append($('<div></div>')
                        .addClass('portlets')
                        .sortable({
                             placeholder: 'portlet-highlight',
                             connectWith: '.portlets',
                             over: MyAMS.portal.template.overPortlets,
                             stop: MyAMS.portal.template.sortPortlets
                        })
                        .droppable({
                             accept: '.btn-portlet',
                             hoverClass: 'portlets-hover',
                             activeClass: 'portlets-active',
                             drop: MyAMS.portal.template.dropPortletButton
                        }))
                    .append($('<div></div>')
                        .addClass('clearfix'));
            const slotButton = $('.btn-slot', slots);
            if (slotButton.exists()) {  // Slot added via drag & drop
                slotButton.replaceWith(newSlot);
                $('.slot', slots).each((idx, elt) => {
                    $(elt).removeData();
                });
                MyAMS.portal.template.sortSlots();
            } else {
                newSlot.appendTo(slots);
            }
            $('.slot', slots).resizable({
                start: MyAMS.portal.template.startSlotResize,
                resize: MyAMS.portal.template.resizeSlot,
                stop: MyAMS.portal.template.stopSlotResize,
                handles: 'e'
            });
            slots.sortable('refresh');
        },

        /**
         * New slot drop button
         */
        dropSlotButton: (event, ui) => {
            if (ui.draggable.hasClass('already-dropped')) {
                return;
            }
            ui.draggable.addClass('already-dropped');
            MyAMS.require('modal').then(() => {
                const rowId = ui.helper.parents('.row:first').data('ams-row-id');
                MyAMS.modal.open(`${getLocation()}/add-template-slot.html?form.widgets.row_id=${rowId}`).then((modal) => {
                    $('.hint').tooltip('hide');
                    modal.on('hide.bs.modal', (evt) => {
                        const form = $('form', modal);
                        if (!form.data('submitted')) {
                            $('.already-dropped').remove();
                        }
                    });
                });
            });
        },

        /**
         * Slot resize start
         */
        startSlotResize: (event, ui) => {
            const
                slot = ui.element,
                row = slot.parents('.slots:first'),
                colWidth = row.innerWidth() / 12,
                slotHeight = slot.height();
            ui.element.resizable('option', 'grid', [colWidth, slotHeight]);
            ui.element.resizable('option', 'minWidth', 10);
            ui.element.resizable('option', 'minHeight', slotHeight);
            ui.element.resizable('option', 'maxWidth', row.innerWidth());
            ui.element.resizable('option', 'maxHeight', slotHeight);
        },

        /**
         * Slot resizing
         */
        resizeSlot: (event, ui) => {
            const
                slot = ui.element,
                row = slot.parents('.slots:first'),
                colWidth = row.innerWidth() / 12,
                width = Math.round(ui.size.width / colWidth),
                device = $('#device_selector').val();
            slot.removeClassPrefix('col-')
                .removeAttr('style')
                .addClass(`col-${device}-${width}`);
        },

        /**
         * Slot resizing end
         */
        stopSlotResize: (event, ui) => {
            const
                slot = ui.element,
                row = slot.parents('.slots:first'),
                colWidth = row.innerWidth() / 12,
                slotCols = Math.round($(slot).width() / colWidth),
                device = $('#device_selector').val();
            MyAMS.require('ajax').then(() => {
                MyAMS.ajax.post(`${getLocation()}/set-slot-width.json`, {
                    slot_name: slot.data('ams-slot-name'),
                    device: device,
                    width: slotCols
                }).then((result) => {
                    slot.removeClassPrefix('col-');
                    slot.removeAttr('style');
                    const slotName = slot.data('ams-slot-name');
                    const widths = result[slotName];
                    slot.addClass(`col-${device}-${widths[device]}`)
                        .addClass(widths.css);
                });
            });
        },

        /**
         * Edit slot properties
         */
        editSlot: (evt) => {
            let slot = $(evt.target);
            if (!slot.hasClass('slot')) {
                slot = slot.parents('.slot');
            }
            MyAMS.require('modal').then(() => {
                MyAMS.modal.open(`${getLocation()}/slot-properties.html?form.widgets.slot_name=${slot.data('ams-slot-name')}`);
            });
        },

        /**
         * Slot edit callback
         */
        editSlotCallback: (form, result) => {
            const slot = $(`.slot[data-ams-slot-name="${result.slot_name}"]`);
            slot.attr('class', 'slot px-0 col');
            const device = $('#device_selector').val();
            if (device) {
                slot.addClass(`col-${result.width[device]}`);
            } else {
                for (const device in result.width) {
                    if (!result.width.hasOwnProperty(device)) {
                        continue;
                    }
                    slot.addClass(`col-${device}-${result.width[device]}`);
                }
            }
            slot.addClass(result.css);
        },

        /**
         * Slot drag over
         */
        overSlots: (event, ui) => {
            $(ui.placeholder)
                .attr('class', $(ui.item).attr('class'))
                .removeClassPrefix('ui-')
                .addClass('slot-highlight')
                .css('height', $(ui.item).outerHeight());
        },

        /**
         * Slots sorting
         */
        sortSlots: (event, ui) => {
            if (ui && ui.item.hasClass('already-dropped')) {
                return;
            }
            const config = $('#portal_config');
            const order = {};
            $('.row', config).each((idx, elt) => {
                const row = $(elt);
                const rowConfig = [];
                $('.slot', row).each((idx, slot) => {
                    rowConfig.push($(slot).data('ams-slot-name'));
                });
                order[parseInt(row.attr('data-ams-row-id'))] = rowConfig;
            });
            MyAMS.require('ajax').then(() => {
                MyAMS.ajax.post(`${getLocation()}/set-template-slot-order.json`,
                    {order: JSON.stringify(order)});
            });
        },

        /**
         * Slot display switch
         */
        switchSlot: (evt) => {
            const
                switcher = $(evt.currentTarget),
                portlets = switcher.parents('.header').first().siblings('.portlets');
            if (portlets.hasClass('hidden')) {
                portlets.removeClass('hidden');
                MyAMS.core.switchIcon(switcher, 'plus-square', 'minus-square');
            } else {
                portlets.addClass('hidden');
                MyAMS.core.switchIcon(switcher, 'minus-square', 'plus-square');
            }
        },

        /**
         * Slot visibility switch
         */
        switchSlotVisibility: (evt) => {
            const target = $(evt.currentTarget);
            let icon = target.objectOrParentWithClass('action');
            const slot = icon.objectOrParentWithClass('slot');
            icon.tooltip('hide');
            icon.replaceWith('<i class="action ml-2 fas fa-fw fa-spinner fa-spin"></i>');
            MyAMS.require('ajax').then(() => {
                MyAMS.ajax.post(`${getLocation()}/switch-slot-visibility.json`, {
                    slot_name: slot.data('ams-slot-name')
                }).then((result) => {
                    icon = $('.fa-spin', slot).objectOrParentWithClass('action');
                    if (result.status) {
                        $('.portlets', slot).removeClass('opacity-50');
                        icon.replaceWith('<i class="action ml-2 fas fa-fw fa-eye hint" ' +
                                         `   data-original-title="${MyAMS.portal.i18n.SWITCH_SLOT_VISIBILITY}" ` +
                                         '   data-ams-click-handler="MyAMS.portal.template.switchSlotVisibility"></i>');
                    } else {
                        $('.portlets', slot).addClass('opacity-50');
                        icon.replaceWith('<i class="action ml-2 fas fa-fw fa-eye-slash text-danger hint" ' +
                                         `   data-original-title="${MyAMS.portal.i18n.SWITCH_SLOT_VISIBILITY}" ` +
                                         '   data-ams-click-handler="MyAMS.portal.template.switchSlotVisibility"></i>');
                    }
                });
            });
        },

        /**
         * Slot delete
         */
        deleteSlot: (evt) => {
            const
                slot = $(evt.currentTarget).objectOrParentWithClass('slot'),
                portlets = $('.portlet', slot);
            MyAMS.require('alert').then(() => {
                if (portlets.exists()) {
                    MyAMS.alert.messageBox({
                        status: 'error',
                        title: MyAMS.i18n.ERROR_OCCURED,
                        content: MyAMS.portal.i18n.CANT_DELETE_SLOT_WITH_PORTLETS
                    });
                } else {
                    MyAMS.alert.bigBox({
                        status: 'danger',
                        title: MyAMS.i18n.WARNING,
                        message: MyAMS.i18n.DELETE_WARNING,
                        icon: 'fas fa-bell'
                    }).then((result) => {
                        if (result === 'success') {
                            MyAMS.require('ajax').then(() => {
                                MyAMS.ajax.post(`${getLocation()}/delete-template-slot.json`, {
                                    slot_name: slot.data('ams-slot-name')
                                }).then((result) => {
                                    if (result.status === 'success') {
                                        slot.remove();
                                        $('.slot', '#portal_config').each((idx, elt) => {
                                            $(elt).removeData();
                                        });
                                    }
                                });
                            });
                        }
                    });
                }
            });
        },


        /**
         * Portlets management
         */

        addPortlet: () => {
            return function(src) {
                $(src).parents('.dropdown').dropdown('hide');
                MyAMS.require('modal').then(() => {
                    MyAMS.modal.open(`${getLocation()}/add-template-portlet.html`);
                });
            }
        },

        /**
         * Portlet add callback
         */
        addPortletCallback: (form, result) => {
            const
                portlets = $('.portlets', `.slot[data-ams-slot-name="${result.slot_name}"]`),
                portlet = $('<div></div>')
                    .addClass('portlet')
                    .attr('data-ams-portlet-id', result.portlet_id)
                    .append(result.preview || '');
            MyAMS.core.initContent($('.preview', portlet)).then(() => {
                const portletButton = $('.btn-portlet', portlets);
                if (portletButton.exists()) {  // Portlet added via drag & drop
                    portletButton.replaceWith(portlet);
                    $('.portlet', portlets).each((idx, elt) => {
                        $(elt).removeData();
                    });
                    MyAMS.portal.template.sortPortlets(null, {item: portlet});
                } else {
                    portlet.appendTo(portlets);
                }
                portlets.sortable('refresh');
                MyAMS.require('modal').then(() => {
                    MyAMS.modal.open(`${getLocation()}/portlet-properties.html?form.widgets.portlet_id=${result.portlet_id}`).then((modal) => {
                        modal.on('hide.bs.modal', (evt) => {
                            const form = $('form', modal);
                            if (!form.data('submitted')) {
                                MyAMS.portal.template.doDeletePortlet(result.portlet_id);
                            }
                        });
                    });
                });
            });
        },

        dropPortletButton: (event, ui) => {
            const
                source = ui.draggable,
                slot = source.parents('.slot:first');
            if (source.hasClass('already-dropped')) {
                return;
            }
            source.addClass('already-dropped');
            MyAMS.require('ajax').then(() => {
                source.tooltip('hide');
                MyAMS.ajax.post(`${getLocation()}/drop-template-portlet.json`, {
                    portlet_name: source.data('ams-portlet-name'),
                    slot_name: slot.data('ams-slot-name')
                }).then((result) => {
                    MyAMS.ajax.handleJSON(result);
                });
            });
        },

        submitPortletEditForm: (legend) => {
            const
                form = $(legend).parents('form').first(),
                button = $('button[type="submit"]', form).first();
            MyAMS.require('form').then(() => {
                const data = {
                    'autosubmit': true
                }
                data[button.attr('name')] = button.val();
                MyAMS.form.submit(form, {
                    data: data
                });
            });
        },

        editPortlet: (evt) => {
            MyAMS.require('modal').then(() => {
                const portlet = $(evt.currentTarget).objectOrParentWithClass('portlet');
                MyAMS.modal.open(`${getLocation()}/portlet-properties.html?form.widgets.portlet_id=${portlet.data('ams-portlet-id')}`);
            });
        },

        editPortletCallback: (form, result) => {
            if (result.preview) {
                const
                    config = $('#portal_config'),
                    portlet = $(`.portlet[data-ams-portlet-id="${result.portlet_id}"]`, config);
                portlet.html(result.preview);
                MyAMS.core.initContent($('.preview', portlet));
            }
        },

        overPortlets: (event, ui) => {
            $(ui.placeholder).attr('class', $(ui.item).attr('class'))
                             .removeClassPrefix('ui-')
                             .addClass('portlet-highlight')
                             .css('height', $(ui.item).outerHeight());
        },

        sortPortlets: (event, ui) => {
            if (ui.item.hasClass('already-dropped')) {
                return;
            }
            const
                portlet = ui.item,
                toSlot = portlet.parents('.slot'),
                toPortlets = $('.portlet', toSlot),
                order = {
                    from: portlet.data('ams-portlet-id'),
                    to: {
                        slot: toSlot.data('ams-slot-name'),
                        portlet_ids: toPortlets.listattr('data-ams-portlet-id')
                    }
                };
            MyAMS.ajax.post(`${getLocation()}/set-template-portlet-order.json`, {
                order: JSON.stringify(order)
            });
        },

        switchPortlet: (evt) => {
            const
                switcher = $(evt.currentTarget),
                portlet = switcher.parents('.header').first().siblings('.preview');
            if (portlet.hasClass('hidden')) {
                portlet.removeClass('hidden');
                MyAMS.core.switchIcon(switcher, 'plus-square', 'minus-square');
            } else {
                portlet.addClass('hidden');
                MyAMS.core.switchIcon(switcher, 'minus-square', 'plus-square');
            }
        },

        /**
         * Delete portlet
         */
        deletePortlet: (evt) => {
            MyAMS.require('alert').then(() => {
                MyAMS.alert.bigBox({
                    status: 'danger',
                    title: MyAMS.i18n.WARNING,
                    message: MyAMS.i18n.DELETE_WARNING,
                    icon: 'fas fa-bell'
                }).then((result) => {
                    const portlet = $(evt.currentTarget).objectOrParentWithClass('portlet');
                    if (result === 'success') {
                        MyAMS.portal.template.doDeletePortlet(portlet.data('ams-portlet-id'));
                    }
                });
            });
        },

        doDeletePortlet: (portletId) => {
            MyAMS.require('ajax').then(() => {
                MyAMS.ajax.post(`${getLocation()}/delete-template-portlet.json`, {
                    portlet_id: portletId
                }).then((result) => {
                    if (result.status === 'success') {
                        const portlet = $(`.portlet[data-ams-portlet-id="${portletId}"]`);
                        portlet.remove();
                        $('.portlet', '#portal_config').each(function() {
                            $(this).removeData();
                        });
                    }
                });
            });
        }
    },

    /**
     * Portal context presentation management
     */
    presentation: {

        handleChange: true,

        resetTemplate: function(evt) {
            MyAMS.portal.presentation.handleChange = false;
        },

        setSharedTemplate: (evt) => {
            if (MyAMS.portal.presentation.handleChange) {
                const form = $(evt.target).parents('form');
                $('input[id="shared_template_mode"]', form).prop('checked', true);
            }
            MyAMS.portal.presentation.handleChange = true;
        }
    }
};


if (window.MyAMS) {
    MyAMS.config.modules.push('portal');
    MyAMS.portal = portal;
    console.debug("MyAMS: portal module loaded...");

    const
        html = $('html'),
        lang = html.attr('lang') || html.attr('xml:lang');
    if (lang && !lang.startsWith('en')) {
        MyAMS.core.getScript(`/--static--/pyams_portal/js/i18n/layout-${lang.substr(0, 2)}.js`);
    }
}
