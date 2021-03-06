# node-wwindowskill
[![NPM version](https://img.shields.io/npm/v/wwindowskill.svg)](https://www.npmjs.com/package/wwindowskill) [![Build Status](https://travis-ci.org/alirdn/node-wwindowskill.svg?branch=master)](https://travis-ci.org/alirdn/node-wwindowskill) [![Build status](https://ci.appveyor.com/api/projects/status/ckerpyyjyuxyoija?svg=true)](https://ci.appveyor.com/project/alirdn/node-wwindowskill) [![codecov](https://codecov.io/gh/alirdn/node-wwindowskill/branch/master/graph/badge.svg?)](https://codecov.io/gh/alirdn/node-wwindowskill) [![Known Vulnerabilities](https://snyk.io/test/github/alirdn/node-wwindowskill/badge.svg?targetFile=package.json)](https://snyk.io/test/github/alirdn/node-wwindowskill?targetFile=package.json) [![GitHub license](https://img.shields.io/github/license/alirdn/node-wwindowskill.svg)](https://github.com/alirdn/node-wwindowskill/blob/master/LICENSE)

Enhance node's ```process.kill``` to support signals in Windows

## Installation
```
$ npm install wwindowskill
```

## Features
* No code change is needed. Just old ```process.kill``` calls.
* Support Both x86 & x64 Windows
* No effect on ***Non Windows*** operation systems (Linux, Mac OS X, etc...)
* Support both ```SIGINT``` and ```SIGBREAK``` (Just the two signals that are available on Windows)

## Why wwindowskill?
Sending signal to another process, just by knowing it's PID, is not available at Windows OS. It's a POSIX OSes feature. But, sending signal to other process, for telling it that something is going to happen to you, is a way to give other process some time for graceful shutdown/restart. wwindowskill tries to fix this issue by bringing the ability to send signals, ```SIGINT``` and ```SIGBREAK```, to another process by **PID**.

## How it works?
To read a detailed info please visit [wwindowskill-library Readme](https://github.com/alirdn/wwindowskill/tree/master/wwindowskill-library#how-it-works).

### Limitations
To send the signal, **wwindowskill** at first send a same signal to the process that is calling it, to find a thread address. Then the founded address is used to send the real signal. Because of this, the process that is sending the signal will get the same signal too. But wwindowskill register a signal handle during this procedure, so the process will not terminate. But if the process that is sending signal has child process, or is a child process of another process, sending signal will trigger the signal handles in other process in the same process group. And the default behavior of Windows console/application in case of getting a ```SIGINT``` or ```SIGBREAK```, is to terminate.

**sum up**: If you are sending signal in node app that has child process (any kind of it), or is a child process of another process, the result is the termination of all the processes in the same process group, except the sender (well if it's a child process, because the master is terminated, it will terminate too).

**PS**: ~~Currently there is no solution for this problem. But I'm working on it, to find a solution.~~ Solutions for different scenarios added.
* [Parent process only send signal](#parent-process-only-send-signal)
* [Cluster master only send signal](#cluster-master-only-send-signal)

**PS-1**: ~~A solution for parent processes that wants to send signal (no way for child processes currently), is added. It's setting the ```warmUp: true``` option when first calling the wwindowskill in parent, before any child processes creation.~~

## Usage
```wwindowskill``` expose a function. Simply run the exposed function with/without the options. Thats it. It should be called before any usage of ```process.kill```.

By default, ```wwindowskill``` will enhance the node's process.kill in a way, that no code changes are needed in your codebase. Enhance means that ```wwindowskill``` will replace the node's ```process.kill``` with a custom function with the same arguments and functionality. Just some changes to achieve signaling in Windows.

### Simplest usage
The returned function from calling the exported function, could be used to send signal, just like the way you call ```process.kill```. It will accept two argument. a ```PID``` and a ```SIGNAL```.

```javascript
/*
    Require and call the function that's exported.
    The returned function can be used to send signal.
*/
var windowsKill = require('wwindowskill')();

/*
    By default, process.kill is enhanced (only in Windows OS),
    so you can either call process.kill, or the returned function.
*/
process.kill(PID, SIGNAL);
windowsKill(PID, SIGNAL);
```

```javascript
/*
    Just call the function, and no need to change any code.
    Every process.kill calls in your code, will now enhanced.
    Just need to call wwindowskill, before any call of
    process.kill.
*/
require('wwindowskill')();

process.kill(PID, SIGNAL);
```

### Options
Options and default values are:

```javascript
const defaultOptions = {
    replaceNodeKill: true,
    warmUp: false
};
```

#### replaceNodeKill
This option will tell the wwindowskill that should it enhance/replace the nodes process.kill? By setting true (default value), the nodes process.kill will replaced by a custom function. This custom function will check the signal that is sending using process.kill. If the signal is a member of supported signals, which is ```SIGINT``` or ```SIGBREAK```, it will call the modules function that is responsible for sending signal. Otherwise, the signal and pid will be passed to the node's original process.kill.

```javascript
const options = {
    replaceNodeKill: true, // Should wwindowskill enhance/replace node's process.kill? Default: true
};

require('wwindowskill')(options);

process.kill(PID, SIGNAL);
```

```javascript
const options = {
    replaceNodeKill: false // Should windows kill enhance/replace node's process.kill. Default: true
};

var windowsKill = require('wwindowskill')(options);

windowsKill(PID, SIGNAL);
```

#### warmUp
By setting warmUp to ```true```, wwindowskill will find and save the ```ctrl-routine``` addresses, without any need to send signal. By default, the address will find, when the first signal of that type is sending. Future call will use the founded address.

```javascript
const options = {
    warmUp: true, // Should wwindowskill warm-up by finding the ctrl-routines addresses? Default: false
};

require('wwindowskill')(options);

process.kill(PID, SIGNAL);
```

Warm-up, is one way to overcome the limitations. Setting this option, will make the wwindowskill to find needed address, before any signal sending. As stated in limitations section, finding address will cause the processes that have child process, or is a child process, trigger the ```ctr-routine``` of all process group members, which means termination of all of them. But warm-up mechanism can be used, to fix the issue in parent process. By setting it to ```true```, before any child process creation, sending signal in future will use the save addresses and no need to find addresses again.

##### Parent process only send signal

```javascript
var options = {
    warmUp: false
};

var cp = require('child_process');
var windowsKill = require('wwindowskill')(options);

var cp1 = cp.spawn('node', ['cp.js']);

windowsKill(PID, 'SIGINT');
```

By running the above code, the cp1 child process will terminate. Because the ```SIGINT``` signal is sent for the first time, and the ```ctrl-routine``` address in not available. So wwindowskill will try to find it, and trying to find it will trigger the ```SIGINT``` handler of cp1 child process, which lead to termination of cp1.

To solve the issue, we can set the ```warmUp``` option ```true```. Just remember, the initialization of wwindowskill with warmUp option should be done before any child process creation. Like below:

```javascript
var options = {
    warmUp: true
};

var cp = require('child_process');
var windowsKill = require('wwindowskill')(options);

var cp1 = cp.spawn('node', ['cp.js']);

windowsKill(PID, 'SIGINT');
```
##### Cluster master only send signal
To avoid the termination of child processes (forks), you should use warmUp option in the master creation part.

```javascript
var cluster = require('cluster');
var os = require('os');

if (cluster.isMaster) {
    /*
        Initialize wwindowskill here. Before and child process creation,
        just in the master process code.
    */
    var windowsKill = require('wwindowskill')({
        "warmUp": true
    });

    for (let i = 0; i < os.cpus().length; i++) {
        cluster.fork();
    }
} else {
    /* Child Process code, that is not using wwindowskill*/
}
```

## Contributing
We love contributions from everyone. Please read [Contributing guide](https://github.com/alirdn/node-wwindowskill/blob/master/CONTRIBUTING.md).

## License
[MIT](https://github.com/alirdn/node-wwindowskill/blob/master/LICENSE)
