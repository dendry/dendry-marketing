#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import subprocess
import shutil
import yaml
import re

BASE_DIRY = os.path.abspath(os.path.dirname(__file__))
TITLE_RE = re.compile(r"<title>(.*?)</title>")
END_OF_PAGE_RE = re.compile(r"\s*</body>")

RIBBON = """
<!-- Inserted by the Dendry website creator. -->
<link rel="stylesheet" href="/css/corner-ribbon.css">
<script src="/js/example-ribbon.js"></script>
"""

class _SampleMaker(object):
    def __init__(self, 
                 base_diry=BASE_DIRY,
                 website_diry='dendry.org',
                 destination_diry="dendry.org/out/examples"):
        self.samples = []
        self.slugs = set()
        self.base_diry = os.path.abspath(base_diry)
        self.website_diry = os.path.abspath(website_diry)
        self.destination_diry = os.path.abspath(
            os.path.join(self.base_diry, destination_diry)
            )

    def _build_sample(self,
                      sample_dir, 
                      slug=None,
                      dendry_cli="../../dendry/lib/cli/main.js",
                      dendry_args=[]):

        """Given a sample or example file in the given directory, this
        compiles it to HTML and copies the output into a subdirectory of the
        website's  examples."""

        if slug is None:
            slug = os.path.split(sample_dir)[-1]
        if slug in self.slugs:
            raise ValueError("Can't create two samples called '%s'" % slug)

        diry = os.path.join(self.base_diry, sample_dir)
        if not os.path.exists(diry):
            raise ValueError("No such directory: '%s'" % diry)
        print "Building sample", repr(slug), "from", repr(diry)

        # Build the html game.
        dendry_path = os.path.join(self.base_diry, dendry_cli)
        subprocess.call([dendry_path, 'make-html'] + dendry_args, cwd=diry)

        # Remove any current content, and copy in the built game files.
        source_diry = os.path.join(diry, 'out', 'html')
        target_diry = os.path.join(self.destination_diry, slug)
        if os.path.exists(target_diry):
            shutil.rmtree(target_diry)
        shutil.copytree(source_diry, target_diry)

        # Find the title of the example's page.
        index_path = os.path.join(target_diry, 'index.html')
        index_content = open(index_path, 'r').read()
        match = TITLE_RE.search(index_content)
        assert match
        title_and_author = match.group(1)
        title, author = title_and_author.split(' - ')
        sample_data = dict(slug=slug, title=title, author=author)
        self.samples.append(sample_data)
        self.slugs.add(slug)

        # TODO: Insert a ribbon to let the user go back to the examples page,
        # or jump to the example on github.
        match = END_OF_PAGE_RE.search(index_content)
        assert match
        index_content = index_content[:match.start(0)] + (
            RIBBON.format(**sample_data)
            ) + index_content[match.start(0):]
        open(index_path, 'w').write(index_content)

    def _build_all_samples_in_repo(self, sample_diry):
        """Given the repository of all samples, builds any that haven't been
        built already."""
        full_sample_diry = os.path.join(self.base_diry, sample_diry)
        samples = [
            name
            for name in os.listdir(full_sample_diry)
            if not name.startswith('.') and
               os.path.isdir(os.path.join(full_sample_diry, name))
            ]
        for sample in samples:
            if sample in self.slugs:
                print "Explicitly created", sample, "- skipping it now"
            else:
                self._build_sample(os.path.join(sample_diry, sample))

    def _create_sample_data(self):
        """The list of samples will be used in a Jekyll template to create
        a page with sample urls, we need to create that."""
        data_dir = os.path.join(self.website_diry, 'src', '_data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        sample_out = sorted(self.samples, lambda a,b: cmp(a['slug'], b['slug']))
        filename = os.path.join(data_dir, 'samples.yaml')
        with open(filename, 'w') as f:
            f.write(yaml.dump(sample_out))
        print "Created data file", repr(filename)

DOC_PREAMBLE = """---
layout: doc
title: Documentation
---
"""

def _fetch_documentation_set(full_doc_diry, full_dest_diry, doc_set_name):
    doc_path = os.path.join(full_doc_diry, doc_set_name)
    dest_path = os.path.join(full_dest_diry, doc_set_name)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    for doc_name in os.listdir(doc_path):
        if doc_name.endswith('.md'):
            this_doc_path = os.path.join(doc_path, doc_name)
            doc_content = DOC_PREAMBLE + open(this_doc_path, 'r').read()
            this_dest_path = os.path.join(dest_path, doc_name)
            open(this_dest_path, 'w').write(doc_content)

def _fetch_documentation(base_diry=BASE_DIRY,
                         doc_diry="../../dendry/doc",
                         destination_diry="dendry.org/src/doc"):
    full_doc_diry = os.path.abspath(os.path.join(BASE_DIRY, doc_diry))
    full_dest_diry = os.path.abspath(os.path.join(base_diry, destination_diry))
    if os.path.exists(full_dest_diry):
        shutil.rmtree(full_dest_diry)

    # Documentation is in subdirectories
    for doc_set_name in os.listdir(full_doc_diry):
        doc_set_path = os.path.join(full_doc_diry, doc_set_name)
        if os.path.isdir(doc_set_path):
            _fetch_documentation_set(full_doc_diry, full_dest_diry, doc_set_name)

def _build_design(base_diry=BASE_DIRY):
    """Creates any icons and imaages from SVG files."""
    design_diry = os.path.join(base_diry, '..', 'design')
    subprocess.call(['make'], cwd=design_diry)

def _build_jekyll_site(website_diry='dendry.org',
                       base_diry=BASE_DIRY):
    """Calls Jekyll to create the main site."""
    full_website_diry = os.path.abspath(os.path.join(base_diry, website_diry))
    subprocess.call(['jekyll', 'build'], cwd=full_website_diry)



# ---------------------------------------------------------------------------

def run(args):
    repo_diry = '../..'

    # Remove any existing site files
    destination_diry="dendry.org/out"
    if os.path.exists(destination_diry):
        shutil.rmtree(destination_diry)

    # Import and augment documentation
    _fetch_documentation()
        
    # Build samples
    sample_maker = _SampleMaker()
    sample_maker._build_sample(
        os.path.join(repo_diry, "bee"),
        dendry_args=['--overwrite']
        )
    # Create any samples from the repo that need particular setup.
    sample_diry = os.path.join(repo_diry, 'samples')
    sample_maker._build_sample(
        os.path.join(sample_diry, "tutorial"),
        dendry_args=['-t', 'onepage']
        )
    # Create anything else in the repo.
    sample_maker._build_all_samples_in_repo(sample_diry)
    # Create the yaml file with the list of created samples.
    sample_maker._create_sample_data()

    # Build images from SVG / high resolution
    _build_design()

    # Create templated website.
    _build_jekyll_site()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Builds the Dendry.org site.")
    
    args = parser.parse_args()
    run(args)

if __name__ == '__main__':
    main()