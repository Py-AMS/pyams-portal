====================
PyAMS portal package
====================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_. Doctests are available in the *doctests* source folder.


What is PyAMS portal?
=====================

PyAMS_portal is a PyAMS extension package which can be used to handle presentation templates.

A template is made of rows, slots and portlets, following Bootstrap's grid logic, and
can be shared between several contexts to handle data or content presentation.

PyAMS_portal package only provides a very small set of portlets. More portlets are provided by
content management packages like PyAMS_content, while other extension packages can be used to
provide custom portlets renderers.
