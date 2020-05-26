#!/usr/bin/groovy

@Library(['github.com/indigo-dc/jenkins-pipeline-library@1.3.6']) _

def deep_oc_build = false

pipeline {
    agent {
        label 'python'
    }

    parameters {
        booleanParam(
            name: 'disable_oc_build',
            defaultValue: false,
            description: 'Force-disable build of the DEEP marketplace'
        )
    }
    
    stages {
        stage('Fetch repository') {
            steps {
                checkout scm: [
                        $class: 'GitSCM',
                        branches: scm.branches,
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [[$class: 'SubmoduleOption',
                                      disableSubmodules: false,
                                      parentCredentials: false,
                                      recursiveSubmodules: true,
                                      reference: '',
                                      trackingSubmodules: false]],
                        submoduleCfg: [],
                        userRemoteConfigs: scm.userRemoteConfigs
                ]
            }
        }
        //stage('repository') {
        //    steps {
        //        sh 'cat .git/config'
        //    }
        //}
        
        stage('Align Git submodules with DEEP modules') {
            when {
                //branch 'master'
                branch 'test-submodules-checkout'
            }
            steps {
                withCredentials([string(
                        credentialsId: "indigobot-github-token",
                        variable: "GITHUB_TOKEN")]) {
                    sh 'git remote set-url origin "https://indigobot:${GITHUB_TOKEN}@github.com/deephdc/deep-oc"'
                    sh 'git config user.name "indigobot"'
                    sh 'git config user.email "<>"'
                    //script { deep_oc_build = alignModules() }
                    script { deep_oc_build = alignModules2() }
                }
            }
        }

        stage('Trigger DEEP marketplace build') {
            when {
                allOf {
                    branch 'master'
                    expression { return deep_oc_build }
                    not { expression { return params.disable_oc_build } }
                }
            }
            steps {
                script {
                    def job_result = JenkinsBuildJob("Pipeline-as-code/deephdc.github.io/pelican")
                    job_result_url = job_result.absoluteUrl
                }
            }
        }

        stage('Trigger update of DEEP applications through OpenWhisk') {
            when {
                allOf {
                    branch 'master'
                    not { expression { return params.disable_oc_build } }
                }
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'openwhisk-token', variable: 'the_token')]) {
                        the_url = "https://deepaas.deep-hybrid-datacloud.eu/api/v1/web/deepaas/deep-oc/update.text"
                        resp = sh(returnStdout: true, script: "curl -X POST \"${the_url}?auth=${the_token}\"")
                        println(resp)
                    }
                }
            }
        }
    }
}


/* methods */
boolean alignModules() {
    def modules_deep_map = [:]
    
    // Get list of DEEP modules 
    data = readYaml (file: 'MODULES.yml')
    data.each{
        base_name = sh(returnStdout: true, script: "basename ${it.module}").trim()
        modules_deep_map.put(base_name, it.module)
    }
    
    // Get list of git submodules
    def modules_git = sh(
        script: 'git submodule | awk \'{print $2}\'',
        returnStdout: true
    ).trim().split()
    
    // Get the git submodules to remove
    def modules_deep_map_keys = modules_deep_map.keySet() as List
    def modules_git_del = []
    modules_git.each {
        if (!(it in modules_deep_map_keys)) {
            modules_git_del.add(it)
        }
    }
    echo ">>> GIT SUBMODULES (to remove): $modules_git_del"
    
    // Remove git submodules
    modules_git_del.each {
        sh(script: "bash tools/remove-module.sh ${it}")
    }

    // Update git submodules to the last version
    sh 'git pull --recurse-submodules'
    sh 'git submodule update --remote --recursive'
    modules_git_update = sh(returnStdout: true, script: 'git status --porcelain=v1')
    if (modules_git_update) {
    	sh 'git commit -a -m "Submodules updated"'
    }
    
    // Add missing modules from MODULES.yml
    modules_deep_add = []
    any_add_failure = false
    modules_deep_map.each {
        if (!fileExists(it.key)) {
            try {
                sh "git submodule add $it.value"
                modules_deep_add.add(it.key)
            }
            catch (e) {
                any_add_failure = true
            }
        }
    }
    echo ">>> DEEP MODULES (to add): $modules_deep_add"
    if (modules_deep_add) {
        sh "git commit -m \"Submodule/s added: $modules_deep_add\""
    }
    
    // Unstable build if there was any failure adding modules
    if (any_add_failure) {
        echo "There were errors adding modules. Setting the build status as UNSTABLE"
        currentBuild.result = 'UNSTABLE'
    }

    // Align OpenWhisk actions with MODULES.yml
    def openwhisk_actions_ignore = ['list', 'update', 'swagger-links']
    def modules_deep_map_keys_unprefixed = []
    modules_deep_map_keys.each {
        // Filter modules without keywords 'pre-trained' and 'api-v2' in the metadata
        def app_metadata = readJSON file: it + '/metadata.json'
        if (('pre-trained' in app_metadata.keywords) && ('api-v2' in app_metadata.keywords)) {
            modules_deep_map_keys_unprefixed.add(it.replaceFirst('DEEP-OC-', ''))
        }
    }
    
    def actions_openwhisk_del = []
    openwhisk_data = readYaml (file: 'openwhisk/manifest.yml')
    openwhisk_data.packages['deep-oc']['actions'].each {
        if ((!(it.key in modules_deep_map_keys_unprefixed)) && (!(it.key in openwhisk_actions_ignore))) {
            actions_openwhisk_del.add(it.key)
        }
    }
    echo ">>> OPENWHISK ACTIONS (to remove): $actions_openwhisk_del"
    actions_openwhisk_del.each {
        openwhisk_data.packages['deep-oc']['actions'].remove(it)
    }
    
    def actions_openwhisk_keys = openwhisk_data.packages['deep-oc']['actions'].keySet() as List
    def actions_openwhisk_add = modules_deep_map_keys_unprefixed - actions_openwhisk_keys
    actions_openwhisk_add.each {
        openwhisk_data.packages['deep-oc']['actions'].put(it, [version:1.0, limits: [memorySize: 2048, timeout: 180000], web:true, docker: "deephdc/deep-oc-${it}:cpu"])
    }
    echo ">>> OPENWHISK ACTIONS (to add): $actions_openwhisk_add"
    echo ">>> OPENWHISK DATA: $openwhisk_data"
 
    if ((actions_openwhisk_del) || (actions_openwhisk_add)) {
    	writeYaml file: 'openwhisk/manifest.yml', data: openwhisk_data, overwrite: true
    	sh 'git commit -a -m "OpenWhisk actions updated"'
    }
    
    // Push changes
    any_commit = modules_git_del || modules_git_update || modules_deep_add || actions_openwhisk_del || actions_openwhisk_add
    if (any_commit) {
        sh 'git push origin HEAD:master'
    }

    return any_commit
}

boolean alignModules2() {
	has_dicom_deep = sh(returnStatus: true, script: "grep dicom MODULES.yml")
    has_dicom_git = sh(returnStatus: true, script: "git submodule | grep dicom")
    has_dicom_openwhisk = sh(returnStatus: true, script: "grep dicom openwhisk/manifest.yml")
    
    dicom_url = "https://github.com/deephdc/DEEP-OC-image-classification-tf-dicom"
    dicom_url_base_name = "DEEP-OC-image-classification-tf-dicom"
    
    openwhisk_data = readYaml (file: 'openwhisk/manifest.yml')

    any_commit = false
    if (has_dicom_deep == 0) {
        //echo ">>>>>>>>>> HAS DICOM DEEP: ${has_dicom_deep}"
        if (has_dicom_git == 1) {
            //echo ">>>>> ADD GIT SUBMODULE <<<<<"
            sh "git submodule add ${dicom_url}"
            sh "git commit -m \"Add ${dicom_url_base_name} submodule\""
            any_commit = true
        }
        // else { update-submodules }
        
        // OPENWHISK
        def app_metadata = readJSON file: dicom_url_base_name + '/metadata.json'
        if (('pre-trained' in app_metadata.keywords) && ('api-v2' in app_metadata.keywords)) {
            //echo ">>>>> ADD OPENWHISK ACTION <<<<<"
            if ( has_dicom_openwhisk == 1 ) {
                openwhisk_data.packages['deep-oc']['actions'].put(
                    'image-classification-tf-dicom', [
                        version:1.0,
                        limits: [memorySize: 2048, timeout: 180000],
                        web:true,
                        docker: "deephdc/deep-oc-image-classification-tf-dicom:cpu"
                    ]
                )
                writeYaml file: 'openwhisk/manifest.yml', data: openwhisk_data, overwrite: true
                sh('git diff openwhisk/manifest.yml')
                sh 'git commit -a -m "Added OpenWhisk action deep-oc-image-classification-tf-dicom"'
                any_commit = true
            }
        }
    }
    else {
        if (has_dicom_git == 0) {
            //echo ">>>>> REMOVE GIT SUBMODULE <<<<<"
            sh(script: "bash tools/remove-module.sh ${dicom_url_base_name}")
            any_commit = true
        }
        
        if (has_dicom_openwhisk == 0) {
            //echo ">>>>> REMOVE OPENWHISK ACTION <<<<<"
            openwhisk_data.packages['deep-oc']['actions'].remove('image-classification-tf-dicom')
    	    writeYaml file: 'openwhisk/manifest.yml', data: openwhisk_data, overwrite: true
            sh 'git commit -a -m "Removed OpenWhisk action deep-oc-image-classification-tf-dicom"'
            any_commit = true
        }
    }
    sh 'git status'
    
    if (any_commit) {
        echo 'Changes done: commiting to master'
        sh 'git push origin HEAD:master'
    }

    return any_commit
}
