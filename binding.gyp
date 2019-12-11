{
    "targets": [
        {
            "target_name": "wwindowskill",
            "product_extension": "node",
            "defines": [ "V8_DEPRECATION_WARNINGS=1" ],
            "include_dirs": [
                "<!(node -e require('nan'))",
                "src/wwindowskill-library/"
            ],
            "libraries": [ "-lDbghelp" ],
            "sources": [
                "src/wwindowskill-library/wwindowskill-library.cpp",
                "src/wwindowskill-library/signal.cpp",
                "src/wwindowskill-library/sender.cpp",
                "src/wwindowskill-library/ctrl-routine.cpp",
                "src/wwindowskill-library/remote-process.cpp",
                "src/wwindowskill-library/stdafx.cpp",
                "src/node-wwindowskill.cpp"
            ],
            "configurations": {
                "Release": {
                    "msvs_settings": {
                        "VCCLCompilerTool": {
                            "ExceptionHandling": 1
                        }
                    }
                },
                "Debug": {
                            "msvs_settings": {
                                "VCCLCompilerTool": {
                                    "ExceptionHandling": 1
                                }
                            }
                        }
            },
            "conditions": [
                ["OS=='win'", {
                    "defines": [
                        "_HAS_EXCEPTIONS=1"
                    ]
                }]
            ]
        },
        {
            "target_name": "action_after_build",
            "type": "none",
            "dependencies": [ "<(module_name)" ],
            "copies": [
            {
                "files": [ "<(PRODUCT_DIR)/<(module_name).node" ],
                "destination": "<(module_path)"
            }
            ]
        }
    ]
}

