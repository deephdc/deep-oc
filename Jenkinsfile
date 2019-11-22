#!/usr/bin/groovy

@Library(['github.com/indigo-dc/jenkins-pipeline-library@1.3.6']) _


pipeline {
    agent {
        label 'python'
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
        
        stage('Align Git submodules with DEEP modules') {
            when {
                branch 'master'
            }
            steps {
                withCredentials([string(
                        credentialsId: "indigobot-github-token",
                        variable: "GITHUB_TOKEN")]) {
                    sh 'git remote set-url origin "https://indigobot:${GITHUB_TOKEN}@github.com/deephdc/deep-oc"'
                    sh 'git config user.name "indigobot"'
                    sh 'git config user.email "<>"'
                    alignModules()
                }
            }
        }

        stage('Trigger DEEP marketplace build') {
            when {
                allOf {
                    branch 'master'
                    changeset '.gitmodules'
                }
            }
            steps {
                script {
                    def job_result = JenkinsBuildJob("Pipeline-as-code/deephdc.github.io/pelican")
                    job_result_url = job_result.absoluteUrl
                }
            }
        }
    }
}


/* methods */
void alignModules() {
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
    	sh 'git commit -m "Update submodules"'
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
        modules_deep_add_str = modules_deep_add.join(', ')
        sh 'git commit -m "Add submodules: $modules_deep_add_str"'
    }
    
    // Unstable build if there was any failure adding modules
    if (any_add_failure) {
        echo "There were errors adding modules. Setting the build status as UNSTABLE"
        currentBuild.result = 'UNSTABLE'
    }
    
    // Push changes
    any_commit = modules_git_del || modules_git_update || modules_deep_add
    if (any_commit) {
        sh 'git push origin HEAD:master'
    }
}
