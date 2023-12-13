Changelog
=========

2.1.0
-----
 - updated modal forms title
 - small updates in template layout row and slot management

2.0.0
-----
 - migrated to Pyramid 2.0

1.9.2
-----
 - updated slots and portlets add menus factories to hide these menus on headers
   and footers layouts when not using a custom template

1.9.1
-----
 - updated doctests

1.9.0
-----
 - added slot CSS class to portlets container
 - updated portlet previewer
 - updated portlet edit form status
 - bypass workflow state check on page preview

1.8.1
-----
 - use new sortable table base class

1.8.0
-----
 - added marker interfaces to handle header and footer templates

1.7.1
-----
 - corrected history syntax error

1.7.0
-----
 - added attribute to portlet settings to define Bootstrap devices on which portlet
   is visible

1.6.2
-----
 - added default portlet settings label adapter
 - removed useless portlets renderers settings adapters
 - updated portlet settings preview templates

1.6.1
-----
 - updated doctests

1.6.0
-----
 - added support for distinct header, body and footer templates in a portlet context
 - added support for Python 3.11
 - added renderer to spacer portlet

1.5.2
-----
 - updated doctests

1.5.1
-----
 - include required Fanstatic resources when portlet content is loaded from cache
 - add request protocol to portlets cache key

1.5.0
-----
 - added default portlet previewer
 - added no-value message to renderer selection widget
 - removed static resources from layout template
 - small refactoring in raw code portlet renderers
 - added *field* and *context* arguments to properties renderers in portlet preview
 - use f-strings instead of format functions (requires Python >= 3.7)
 - updated translations
 - added support for Python 3.10

1.4.4
-----
 - remove empty portlets from portal layout
 - use new ZMI base columns classes in cards and carousel portlets management views

1.4.3
-----
 - added link to image preview in image portlet

1.4.2
-----
 - restored missing callback in template layout

1.4.1
-----
 - updated MyAMS module registration
 - updated renderer selection widget classname
 - use new context base add action

1.4.0
-----
 - added prefix and suffix HTML codes to slot configuration

1.3.3
-----
 - added option to display menu to access templates container from ZMI home page

1.3.2
-----
 - added check for missing portlet renderer in preview
 - updated translation string name in layout management script

1.3.1
-----
 - updated content provider rendering API, adding new "template_name" argument to
   "render" methods

1.3.0
-----
 - added template container CSS class (with custom TALES extension and updated layout)
 - added support for designer role to portal templates container
 - added template properties edit form
 - updated doctests

1.2.3
-----
 - small template layout CSS updates
 - added templates label adapter
 - updated add and edit forms title

1.2.2
-----
 - package version mismatch

1.2.1
-----
 - updated portlets inner settings forms label
 - use IObjectLabel adapter in local template share form

1.2.0
-----
 - added Bootstrap float classes to slots
 - updated Javascript layout handler

1.1.0
-----
 - added feature to create a shared template from a local one
 - removed permission on default portlets
 - updated forms title
 - updated translations

1.0.4
-----
 - clear portlets cache after configuration or renderer settings update

1.0.3
-----
 - updated layout offset classes for XS devices

1.0.2
-----
 - corrected syntax error in image portlet setting
 - updated ZMI modules exclusion rule when including package

1.0.1
-----
 - Javascript code cleanup

1.0.0
-----
 - initial release
