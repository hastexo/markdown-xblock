# markdown XBlock

The markdown [XBlock](https://xblock.readthedocs.org/en/latest/) allows [Open
edX](https://open.edx.org/) course authors to write courseware using
[markdown](http://daringfireball.net/projects/markdown/).


## Deployment

The easiest way for platform administrators to deploy the markdown XBlock and
its dependencies to an Open edX installation is to pip install it to the edxapp
virtualenv.

1. Install it via pip:

    ```
    $ sudo /edx/bin/pip.edxapp install -e git+https://github.com/hastexo/markdown-xblock.git@master#egg=markdown-xblock
    ```

2. Restart edxapp:

    ```
    sudo /edx/bin/supervisorctl restart edxapp:
    ```

3. In your course, go to the advanced settings and add the `markdown` module to 
   the "Advanced Module List" like so:
   ```
   [
    "annotatable",
    "videoalpha",
    "openassessment",
    "markdown"
   ]
   ```

## License

This XBlock is licensed under the Affero GPL; see [`LICENSE`](LICENSE)
for details.
