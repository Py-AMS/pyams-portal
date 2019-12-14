=====================
PyAMS_pagelet package
=====================

.. contents::


What is PyAMS
=============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_


What is PyAMS_pagelet?
======================

This package is a small rewrite of z3c.pagelet package for use with Pyramid.

PyAMS_template allows to separate a view's Python code from it's template implementation, so that
this template can be easilly overriden for a given view or a given layer; it also allows to
separate a "content" template from a "layout" template which is handling all common elements in
a web page.

PyAMS_pagelet is an implementation of this pattern: a pagelet is a Pyramid view registered with
the name of the pagelet; the layout template can then just use a "${structure:provider:pagelet}"
directive to automatically insert the pagelet matching the current browser URL.
