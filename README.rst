.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/keitaroinc/ckanext-orgdashboards.svg?branch=master
    :target: https://travis-ci.org/keitaroinc/ckanext-orgdashboards

.. image:: https://coveralls.io/repos/keitaroinc/ckanext-orgdashboards/badge.svg
  :target: https://coveralls.io/r/keitaroinc/ckanext-orgdashboards

.. image:: https://pypip.in/download/ckanext-orgdashboards/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-orgdashboards/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-orgdashboards/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-orgdashboards/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-orgdashboards/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-orgdashboards/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-orgdashboards/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-orgdashboards/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-orgdashboards/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-orgdashboards/
    :alt: License

=============
ckanext-orgdashboards
=============

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!


------------
Requirements
------------

For example, you might want to mention here which versions of CKAN this
extension works with.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-orgdashboards:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-orgdashboards Python package into your virtual environment::

     pip install ckanext-orgdashboards

3. Add ``orgdashboards`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Add ``ckanext.orgdashboards.datasets_per_page`` as a setting in the config file::

    ckanext.orgdashboards.datasets_per_page = 5

5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

Document any optional config settings here. For example::

    # The minimum number of hours to wait before re-checking a resource
    # (optional, default: 24).
    ckanext.orgdashboards.some_setting = some_default_value


------------------------
Development Installation
------------------------

To install ckanext-orgdashboards for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/keitaroinc/ckanext-orgdashboards.git
    cd ckanext-orgdashboards
    python setup.py develop
    pip install -r dev-requirements.txt

------------------------
Languages Installation
------------------------

In order to use languages that are not supported by CKAN, you have to install
them manually. Open up a terminal inside the CKAN's source directory, and type
the following command to initialize a new catalog for a language::

    python setup.py init_catalog --locale YOUR_LANGUAGE

where ``YOUR_LANGUAGE`` is the locale of the language. This command will 
create a ``.po`` file inside ``ckan/i18n/YOUR_LANGUAGE/LC_MESSAGES``
which contains the strings for the language. 

Next you have to compile tha language into a binary format with the following
command::

    python setup.py compile_catalog --locale YOUR_LANGUAGE

where ``YOUR_LANGUAGE`` is the locale of the language. This command will 
create a ``.mo`` file, and the one which CKAN will read the strings from.

------------------------
Languages Translation
------------------------

If you want to add additional strings for a certain language and translate
them, then follow these instructions:

1. Switch to the extension's directory and add a directory to store your 
translations::

    mkdir ckanext/orgdashboards/i18n

2. Extract the strings from the extension with this 
command::

    python setup.py extract_messages

This will create a template ``.po`` file named 
``ckanext/orgdashboards/i18n/ckanext-orgdashboards.pot``

3. The next step is to create the translations. Let's say that you want to
translate strings for the ``de`` locale. Create the translation ``.po`` file 
for the locale that you are translating for by running ``init_catalog``::

    python setup.py init_catalog -l de

This will generate a file called ``i18n/de/LC_MESSAGES/ckanext-orgdashboards.po``.
It contains every string extracted from the extension. For example, if you want
to translate the string ``Groups``, locate it in the ``.po`` file and type the
appropriate translation::

    msgid "Groups"
    msgstr "Gruppen"

A ``.po`` file can also be edited using a special program for translation called 
`Poedit <https://poedit.net/>`_.

4. Once you are done with translation, next step is to compile the catalog with
the ``compile_catalog`` command::
    
    python setup.py compile_catalog -l de

This will create a binary ``.mo`` file named 
``ckanext/orgdashboards/i18n/ckanext-orgdashboards.mo`` containing your 
translations.

Once you have added the translated strings, you will need to inform CKAN that 
your extension is translated by implementing the ``ITranslation`` interface in
your extension. Edit your ``plugin.py`` to contain the following::

    from ckan.lib.plugins import DefaultTranslation


    class YourPlugin(plugins.SingletonPlugin, DefaultTranslation):
        plugins.implements(plugins.ITranslation)

Restart the server and you should find that switching to the ``de`` locale in 
the web interface should change the ``Groups`` string.

More information on translating extensions can be found on the offical
documentation on CKAN.

-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.orgdashboards --cover-inclusive --cover-erase --cover-tests


---------------------------------
Registering ckanext-orgdashboards on PyPI
---------------------------------

ckanext-orgdashboards should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-orgdashboards. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-orgdashboards
----------------------------------------

ckanext-orgdashboards is availabe on PyPI as https://pypi.python.org/pypi/ckanext-orgdashboards.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
