#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import subprocess
import shutil

BASE_DIRY = os.path.abspath(os.path.dirname(__file__))

def _build_sample(sample_dir, 
                  slug=None,
                  base_diry=BASE_DIRY,
                  dendry_cli="../../dendry/lib/cli/main.js",
                  dendry_args=[],
                  destination_diry="dendry.org/out/examples"):
    """Given a sample or example file in the given directory, this compiles
    it to HTML and copies the output into a subdirectory of the website's 
    examples."""
    if slug is None:
        slug = os.path.split(sample_dir)[-1]

    diry = os.path.abspath(os.path.join(base_diry, sample_dir))
    if not os.path.exists(diry):
        raise ValueError("No such directory: '%s'" % diry)
    print "Building sample", repr(slug), "from", repr(diry)

    # Build the output.
    dendry_path = os.path.abspath(os.path.join(base_diry, dendry_cli))
    subprocess.call([dendry_path, 'make-html'] + dendry_args, cwd=diry)

    # Remove any current output content.
    source_diry = os.path.join(diry, 'out', 'html')
    target_diry = os.path.abspath(
        os.path.join(base_diry, destination_diry, slug)
        )
    if os.path.exists(target_diry):
        shutil.rmtree(target_diry)
    shutil.copytree(source_diry, target_diry)

def _build_samples_repo(sample_diry,
                        base_diry=BASE_DIRY):
    """Given the repository of all samples, builds them one at a time."""
    full_sample_diry = os.path.abspath(os.path.join(base_diry, sample_diry))
    samples = [
        name
        for name in os.listdir(full_sample_diry)
        if not name.startswith('.') and
           os.path.isdir(os.path.join(full_sample_diry, name))
        ]
    for sample in samples:
        _build_sample(os.path.join(sample_diry, sample), base_diry=base_diry)

def _build_jekyll_site(website_diry='dendry.org',
                       base_diry=BASE_DIRY):
    full_website_diry = os.path.abspath(os.path.join(base_diry, website_diry))
    subprocess.call(['jekyll', 'build'], cwd=full_website_diry)

def run(args):
    repo_diry = '../..'
    sample_diry = os.path.join(repo_diry, 'samples')
    #_build_samples_repo(sample_diry)
    #_build_sample(os.path.join(repo_diry, "bee"))
    _build_jekyll_site()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Builds the Dendry.org site.")
    
    args = parser.parse_args()
    run(args)

if __name__ == '__main__':
    main()