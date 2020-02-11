# DEEP Open Catalog

<img src="https://marketplace.deep-hybrid-datacloud.eu/images/logo-deep.png" width=200 alt="DEEP-Hybrid-DataCloud logo"/>

This repository contains the DEEP-Hybrid-DataCloud Open Catalog modules. Feel
free to clone, add your own module and submit it as a pull request for review.

The modules included in this repository are included in the
[DEEP Marketplace](https://marketplace.deep-hybrid-datacloud.eu), where you can
get more information about them (downloading, building, executing, etc.).

# Adding a module to the marketplace

Edit the MODULES.yml file and include it as follows:

    (...)
    - module: https://github.com/deephdc/DEEP-OC-whatever

Once added, submit a pull request to this repo.

You can also make it [online on GitHub](https://github.com/deephdc/deep-oc/edit/master/MODULES.yml).

# Deploying on OpenWhisk

The DEEP Open Catalog can be deployed on an OpenWhisk instance, using the
[wskdeploy](https://github.com/apache/openwhisk-wskdeploy/) software. In order
to do so, you need to create a namespace in your OpenWhisk deployment and get
its API key:

    wskadmin user create deepaas

Then, you are able to deploy the DEEP-OC package as follows:

    wskdeploy -v -p deep-oc/openwhisk

You can verify that the package is deployed, by listing the actions in the
namespace:

    wsk action list

There is a special action `list` that allows you to retrieve the deployed
modules:

    wsk action invoke /deepaas/deep-oc/list --result
