
Vusi's machine                                       Miguel's machine                        GitHub
_______________                                      _______________                         _______________


AI Folder
    - git repository (git init)

    - main/master branch - tags
      - Usually meant for releases
        - tag branches (i.e. v1.0, ...)
    - for work purposes from master, create branch (usually for features) - named
      - add every iteration (git commits w/ message) - messages
      - ...
      - when the feature is developed (and tested) -> PR and merge to the branch where it came from

master
   |
   - feature/branch
     \- commit 1
     \- commit 2
     \- commit 3
     \- commit 4
     \- commit 5
     \- commit 6
     \- commit 7

    - share with others, by uploading to a shared repository
      - git push (origin / remote)

                                                                                                master
                                                                                                |
                                                                                                - feature/branch
                                                                                                    \- commit 1
                                                                                                    \- commit 2
                                                                                                    \- commit 3
                                                                                                    \- commit 4
                                                                                                    \- commit 5
                                                                                                    \- commit 6
                                                                                                    \- commit 7

                                                    - get the latest changes from the remote repository
                                                      - (git pull)
                                                    - position yourself in the branch you want to work
                                                      - git checkout <branch>

                                                    master
                                                    |
                                                    - feature/branch
                                                        \- commit 1
                                                        \- commit 2
                                                        \- commit 3
                                                        \- commit 4
                                                        \- commit 5
                                                        \- commit 6
                                                        \- commit 7
                                                    
                                                    \- commit 8
                                                    \- commit 9

                                                    - share with others, by uploading to a shared repository
                                                      - git push (origin / remote)

                                                                                                master
                                                                                                |
                                                                                                - feature/branch
                                                                                                    \- commit 1
                                                                                                    \- commit 2
                                                                                                    \- commit 3
                                                                                                    \- commit 4
                                                                                                    \- commit 5
                                                                                                    \- commit 6
                                                                                                    \- commit 7
                                                                                                    \- commit 8
                                                                                                    \- commit 9

- get the latest changes from the remote repository
  - (git pull)

master
|
- feature/branch
    \- commit 1
    \- commit 2
    \- commit 3
    \- commit 4
    \- commit 5
    \- commit 6
    \- commit 7
    \- commit 8
    \- commit 9
