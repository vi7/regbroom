import os
import sys
import re
import json
import subprocess
from . import logger as l


def set_config(conf):
    global config
    config = conf

def run_regctl(args, fail_on_error=True):
    """Return the stdout of the regctl tool execution
    and handle possible regctl failures
    """
    cmdline = ['regctl']
    cmdline.extend(args)
    try:
        result = subprocess.run(cmdline, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as err:
        if fail_on_error:
            sys.exit("regctl FAILED!\nExit code: {}\nCmdline: {}\nStdout: {}\nStderr: {}".format
                (
                    err.returncode,
                    ' '.join(err.cmd),
                    err.stdout,
                    err.stderr
                    )
                )
        else:
            l.log("\033[33mWARN: regctl failed with error\nstdout: {}\nstderr: {}\033[0".format(err.stdout, err.stderr))
            l.log("\033[33mWARN: silently skipping this failure\033[0")
    return

def list_tags(repo):
    """Return the list of all available tags for the specified
    Docker repository
    """
    l.log("Fetching tags for the Docker repo {}".format(repo))
    tags_raw = json.loads(run_regctl(["tag", "ls", "--format", "body", repo]))
    tags = tags_raw["tags"] if tags_raw["tags"] else []
    l.log("Total {} tags found".format(len(tags)))
    return tags

def filter_tags(tags, tag_pattern):
    """Return the list of tags matching specified regexp
    pattern
    """
    tag_regex = re.compile(tag_pattern)
    l.log("Filtering tags with pattern \"{}\"".format(tag_pattern))
    tags_filtered = [tag for tag in tags if tag_regex.match(tag)]
    l.log("{} tags found".format(len(tags_filtered)))
    l.log_debug("\n{}".format('\n'.join(tags_filtered)))
    return tags_filtered

def get_release_tags(all_tags, release_pattern, release_keep_count):
    """Return tuple with the tags filtered by the pattern specified
    via 'release_ver_pattern' config option
    ret_val[0] - tags to clean
    ret_val[1] - tags to keep
    """
    l.log('Generating cleanup and keep lists for the RELEASE tags')
    release_tags = filter_tags(all_tags, release_pattern)
    rel_keep_count_norm = 0 if release_keep_count >= len(release_tags) else len(release_tags) - release_keep_count
    rel_tags_clean = release_tags[:rel_keep_count_norm:]
    rel_tags_keep = release_tags[rel_keep_count_norm::]
    return (rel_tags_clean, rel_tags_keep)

def get_dev_tags(all_tags, release_tags_keep, dev_pattern, dev_keep_count):
    """Return tuple with the tags filtered by the pattern specified
    via 'dev_ver_pattern' config option
    ret_val[0] - tags to clean
    ret_val[1] - tags to keep
    """
    l.log('Generating cleanup and keep lists for the DEV tags')
    dev_tags_keep = []
    dev_tags = filter_tags(all_tags, dev_pattern)

    if release_tags_keep:
        rel_tags_keep_rev = list(reversed(release_tags_keep))
        # Prefetch all DEV tags related to the kept RELEASE tags
        # to avoid multiple iterations over the huge list of all DEV tags
        dev_tags_keep_pre = [dev_tag for rel_tag in rel_tags_keep_rev for dev_tag in reversed(dev_tags) if rel_tag in dev_tag]

        # Iterate over reversed lists of the dev and release tags to find
        # the most recent tags faster and keep on
        for rel_tag in rel_tags_keep_rev:
            i = 0
            l.log_debug("Reverse searching DEV tags for the RELEASE {}".format(rel_tag))
            for tag in dev_tags_keep_pre:
                if rel_tag in tag:
                    l.log_debug("DEV tag {} found. Adding to the keep list".format(tag))
                    dev_tags_keep.insert(0, tag)
                    i = i + 1
                    if i == dev_keep_count:
                        break
        dev_tags_clean = [tag for tag in dev_tags if tag not in dev_tags_keep]
    # Ensure to keep at least 'dev_keep_count' when no release tags found
    else:
        dev_keep_count_norm = 0 if dev_keep_count >= len(dev_tags) else len(dev_tags) - dev_keep_count
        dev_tags_clean = dev_tags[:dev_keep_count_norm:]
        dev_tags_keep = dev_tags[dev_keep_count_norm::]

    return (dev_tags_clean, dev_tags_keep)

def delete_image(repo, tag, fail_on_error):
    """Delete docker image (manifest) by tag
    This does not delete the actual data (blobs) from the registry,
    meaning that you must still run 'registry garbage-collect' on your own
    """
    image_url = "{}:{}".format(repo, tag)
    l.log_debug("Removing image {}".format(image_url))
    run_regctl(["tag", "delete", image_url], fail_on_error)

def sweep_repo(repo_url, release_pattern, release_keep_count,
               dev_pattern, dev_keep_count, force, fail_on_error):
    """Run cleanup for the repository with specified parameters
    """
    all_tags = list_tags(repo_url)
    if not all_tags:
        l.log("\033[33mWARN: No matching tags found for the {}. Skipping this repo\033[0m".format(repo_url))
        return

    release_tags = get_release_tags(all_tags, release_pattern, release_keep_count)
    rel_tags_clean = release_tags[0]
    rel_tags_keep = release_tags[1]

    if not rel_tags_clean and not rel_tags_keep and not force:
        l.log("\033[33mWARN: No RELEASE tags found for pattern \"{}\"\n\
        Dev tags with pattern \"{}\" won't be touched at all.\n\
        Set 'force: true' for the image repo config to still cleanup dev tags\n\
        \033[0m".format(release_pattern, dev_pattern))
        return

    l.log("The following {} RELEASE tags will be REMOVED".format(len(rel_tags_clean)))
    l.log_debug("\n{}".format('\n'.join(rel_tags_clean)))
    l.log("The following {} RELEASE tags will be kept".format(len(rel_tags_keep)))
    l.log_debug("\n{}".format('\n'.join(rel_tags_keep)))

    dev_tags = get_dev_tags(all_tags, rel_tags_keep, dev_pattern, dev_keep_count)
    dev_tags_clean = dev_tags[0]
    dev_tags_keep = dev_tags[1]
    l.log("The following {} DEV tags will be REMOVED".format(len(dev_tags_clean)))
    l.log_debug("\n{}".format('\n'.join(dev_tags_clean)))
    l.log("The following {} DEV tags will be kept".format(len(dev_tags_keep)))
    l.log_debug("\n{}".format('\n'.join(dev_tags_keep)))

    if not config['dryrun'].get(bool):
        if not rel_tags_clean:
            l.log("No RELEASE tags for cleanup found")
        else:
            l.log("Performing RELEASE tags cleanup")
            for tag in rel_tags_clean:
                delete_image(repo_url, tag, fail_on_error)

        if not dev_tags_clean:
            l.log("No DEV tags for cleanup found")
        else:
            l.log("Performing DEV tags cleanup")
            for tag in dev_tags_clean:
                delete_image(repo_url, tag, fail_on_error)
    else:
        l.log("\033[1;33mDry run mode enabled. Skipping actual cleanup\033[0;0m")

def sweep():
    """Entrypoint function of the module which fetches provided repository
    configs and launches cleanup for them
    """
    for i in range(len(config['images'].get(list))):
        sweep_repo(config['images'][i]['repo'].get(str),
                   config['images'][i]['release_ver_pattern'].get(str),
                   config['images'][i]['release_ver_keep'].get(int),
                   config['images'][i]['dev_ver_pattern'].get(str),
                   config['images'][i]['dev_ver_keep'].get(int),
                   config['images'][i]['force'].get(bool),
                   config['images'][i]['fail_on_error'].get(bool))

    print("\n\n\033[1;33m[IMPORTANT] Run garbage collection for the Registry to retain the actual disk space!\n\
        See here https://docs.docker.com/registry/garbage-collection/ for the details\033[0;0m\n")
