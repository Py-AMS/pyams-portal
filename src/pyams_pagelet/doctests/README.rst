
=====================
pyams_pagelet package
=====================

Let's start by creating a new template:

    >>> from pyramid.testing import setUp, tearDown
    >>> from pyams_utils.request import get_annotations
    >>> config = setUp()
    >>> config.add_request_method(get_annotations, 'annotations', reify=True)

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
    >>> config.registry.registerAdapter(factory, (Interface, IRequest), IContentTemplate)

    >>> factory = TemplateFactory(layout_template, 'text/html')
    >>> config.registry.registerAdapter(factory, (Interface, IRequest), ILayoutTemplate)

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
    <BLANKLINE>

But the standard way of using a pagelet is by using the "pagelet:" TALES expression:

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
    >>> config.registry.registerAdapter(factory, (IMyView, IRequest), ILayoutTemplate)

    >>> try:
    ...     view()
    ... except Exception as e:
    ...     print(repr(e))
    ContentProviderLookupError('pagelet...)

This exception is raised because the pagelet is not yet registered; this should be done
automatically when *pyams_pagelet* package is included into Pyramid configuration:

    >>> from zope.contentprovider.interfaces import IContentProvider
    >>> from pyams_pagelet.interfaces import IPagelet
    >>> from pyams_pagelet.pagelet import PageletRenderer
    >>> config.registry.registerAdapter(PageletRenderer,
    ...                                 (Interface, IRequest, IPagelet),
    ...                                 IContentProvider, name='pagelet')
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
    <BLANKLINE>

    >>> tearDown()
