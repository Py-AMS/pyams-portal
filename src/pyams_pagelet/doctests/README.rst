
=====================
pyams_pagelet package
=====================

Let's start by creating a new template:

    >>> from pyramid.testing import setUp, tearDown
    >>> from pyams_utils.request import get_annotations

    >>> config = setUp(hook_zca=True)
    >>> config.add_request_method(get_annotations, 'annotations', reify=True)

    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_template import includeme as include_template
    >>> include_template(config)

    >>> import os, tempfile
    >>> temp_dir = tempfile.mkdtemp()

    >>> content_template = os.path.join(temp_dir, 'content-template.pt')
    >>> with open(content_template, 'w') as file:
    ...     _ = file.write('<div>Base template content</div>')

    >>> layout_template = os.path.join(temp_dir, 'layout-template.pt')
    >>> with open(layout_template, 'w') as file:
    ...     _ = file.write('''
    ... <html>
    ...   <body>
    ...     <div class="layout">${structure:view.render()}</div>
    ...   </body>
    ... </html>
    ... ''')

The templates must now be registered for a view and a request. We use the TemplateFactory directly
here from *pyams_template* package, while it may be done using a *template_config* decorator:

    >>> from zope.interface import implementer, Interface
    >>> from pyramid.interfaces import IRequest
    >>> from pyams_template.interfaces import IContentTemplate, ILayoutTemplate

    >>> from pyams_template.template import TemplateFactory
    >>> factory = TemplateFactory(content_template, 'text/html')
    >>> config.registry.registerAdapter(factory, (Interface, IRequest, Interface), IContentTemplate)

    >>> factory = TemplateFactory(layout_template, 'text/html')
    >>> config.registry.registerAdapter(factory, (Interface, IRequest, Interface), ILayoutTemplate)

Let's now create a pagelet view:

    >>> class IMyView(Interface):
    ...     """View marker interface"""

    >>> from pyams_pagelet.pagelet import Pagelet
    >>> @implementer(IMyView)
    ... class MyView(Pagelet):
    ...     """View class"""

    >>> from pyramid.testing import DummyRequest
    >>> content = object()
    >>> request = DummyRequest()
    >>> view = MyView(content, request)
    >>> print(view.render())
    <div>Base template content</div>

    >>> print(view())
    200 OK
    Content-Type: text/html; charset=UTF-8
    Content-Length: 98
    <BLANKLINE>
    <html>
      <body>
        <div class="layout"><div>Base template content</div></div>
      </body>
    </html>

But the standard way of using a pagelet is by using the "provider:pagelet" TALES expression:

    >>> pagelet_template = os.path.join(temp_dir, 'pagelet-template.pt')
    >>> with open(pagelet_template, 'w') as file:
    ...     _ = file.write('''
    ... <html>
    ...   <body>
    ...     <div class="pagelet">${structure:provider:pagelet}</div>
    ...   </body>
    ... </html>
    ... ''')

This template will be registered using the custom view interface:

    >>> from chameleon import PageTemplateFile
    >>> from pyams_viewlet.provider import ProviderExpr
    >>> PageTemplateFile.expression_types['provider'] = ProviderExpr

    >>> factory = TemplateFactory(pagelet_template, 'text/html')
    >>> config.registry.registerAdapter(factory, (Interface, IRequest, IMyView), ILayoutTemplate)

    >>> try:
    ...     view()
    ... except Exception as e:
    ...     print(repr(e))
    ContentProviderLookupError('pagelet...)

This exception is raised because the pagelet is not yet registered; this should be done
automatically when *pyams_pagelet* package is included into Pyramid configuration:

    >>> from pyams_pagelet import includeme as include_pagelet
    >>> include_pagelet(config)

    >>> print(view())
    200 OK
    Content-Type: text/html; charset=UTF-8
    Content-Length: 99
    <BLANKLINE>
    <html>
      <body>
        <div class="pagelet"><div>Base template content</div></div>
      </body>
    </html>


Testing the pagelet decorator
-----------------------------

This package provides a "pagelet_config" decorator, which is working like the classic Pyramid's
"view_config" decorator: it is registering a new view, but is also registering this view as an
IPagelet adapter:

    >>> from pyams_pagelet import includeme as include_pagelet
    >>> include_pagelet(config)

    >>> from pyams_utils.testing import call_decorator
    >>> from pyams_pagelet.pagelet import pagelet_config
    >>> from pyams_template.template import template_config, layout_config

    >>> class AnotherView:
    ...     """Pagelet view"""

    >>> pagelet_template = os.path.join(temp_dir, 'pagelet-template-2.pt')
    >>> with open(pagelet_template, 'w') as file:
    ...     _ = file.write('''<div>Pagelet content</div>''')

    >>> layout_template = os.path.join(temp_dir, 'layout-template-2.pt')
    >>> with open(layout_template, 'w') as file:
    ...     _ = file.write('''
    ... <html>
    ...   <body>
    ...     <div class="layout-2">${structure:provider:pagelet}</div>
    ...   </body>
    ... </html>
    ... ''')

    >>> call_decorator(config, pagelet_config, AnotherView,
    ...                name='testing-2.html',
    ...                for_=Interface,
    ...                layer=IRequest)
    >>> call_decorator(config, template_config, AnotherView,
    ...                template=pagelet_template)
    >>> call_decorator(config, layout_config, AnotherView,
    ...                template=layout_template)

Let's now try to check if this pagelet is correctly registered:

    >>> from pyramid.view import render_view
    >>> print(render_view(content, request, 'testing-2.html').decode())
    <html>
      <body>
        <div class="layout-2"><div>Pagelet content</div></div>
      </body>
    </html>

As view doesn't implement any custom interface, it's inheriting default layout and template!


Tests cleanup:

    >>> tearDown()
