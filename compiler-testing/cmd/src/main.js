#!/usr/bin/env node
import { Command } from 'commander';
import { fileURLToPath } from 'url';
import fs from 'fs';
import path from 'path';
import childProcess from 'child_process';
import { run } from './runner.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

const getConfigNameByVersion = (version) => {
  if (version === '2.1.8') {
    return 'config-default-1';
  }
  return 'config-default-2';
};

const checkVersion = (version) => {
  if (version !== '2.1.8' && version !== '2.0.2') {
    console.log('当前版本号仅支持 2.1.8 和 2.0.2！');
    return false;
  }
  return true;
};

const checkOptions = (options) => {
  if (options.cflags && !['--O0', '--O1', '--O2'].includes(options.cflags)) {
    console.log('当前仅支持 --O0, --O1, --O2 优化级别！不支持其他参数覆盖');
    return false;
  }
  return true;
};

function readJsonFile(filePath) {
  try {
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    console.error(
      `[ERROR] Failed to read JSON file ${filePath}: ${err.message}`
    );
    process.exit(1);
  }
}

function writeJsonFile(filePath, data) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error(
      `[ERROR] Failed to write JSON file ${filePath}: ${err.message}`
    );
    process.exit(1);
  }
}

const generateTempConfigFile = (file, options, dist) => {
  const config = readJsonFile(file);
  config.cflags = options.cflags;
  writeJsonFile(dist, config);
};

function runSingleMode(version, options) {
  const checked = checkOptions(options) && checkVersion(version);
  if (!checked) {
    return;
  }
  const configFile = path.resolve(
    __dirname,
    `../../config/${getConfigNameByVersion(version)}.json`
  );
  const tempConfigFile = path.resolve(
    __dirname,
    `../../temp/${getConfigNameByVersion(version)}-temp.json`
  );
  generateTempConfigFile(configFile, options, tempConfigFile);
  run(tempConfigFile, 'single', {
    versions: [version]
  });
}

function runCrossMode(version1, version2, options) {
  const checked =
    checkOptions(options) && checkVersion(version1) && checkVersion(version2);
  if (!checked) {
    return;
  }
  const configFile = path.resolve(
    __dirname,
    `../../config/${getConfigNameByVersion(version1)}.json`
  );
  const tempConfigFile = path.resolve(
    __dirname,
    `../../temp/${getConfigNameByVersion(version1)}-temp.json`
  );
  generateTempConfigFile(configFile, options, tempConfigFile);
  run(tempConfigFile, 'cross', { versions: [version1, version2] });
}

/**
 * 执行 replay 模式
 */
function runReplayMode(caseName, options) {
  if (!['n1', 'n2', 'n3', 'n4'].includes(caseName)) {
    console.log('当前仅支持 n1, n2, n3, n4 四个已知测试用例！');
    return;
  }
  const cases = {
    n1: path.resolve(__dirname, '../../cases/run1.sh'),
    n2: path.resolve(__dirname, '../../cases/run2.sh'),
    n3: path.resolve(__dirname, '../../cases/run3.sh'),
    n4: path.resolve(__dirname, '../../cases/run4.sh')
  };
  const caseFile = cases[caseName];
  childProcess.execSync(`${caseFile}`, {
    stdio: 'inherit'
  });
}

// 配置程序信息
program
  .name('circom-test')
  .description('CLI tool for testing Circom compiler versions')
  .version('1.0.0');

// Single mode command
program
  .command('single <version>')
  .description('Test a single Circom compiler version')
  .option(
    '--cflags <flags>',
    'Compiler optimization flags (--O0, --O1, --O2)',
    '--O1'
  )
  .action(runSingleMode);

// Cross mode command
program
  .command('cross <version1> <version2>')
  .description('Test across two Circom compiler versions')
  .option(
    '--cflags <flags>',
    'Compiler optimization flags (--O0, --O1, --O2)',
    '--O1'
  )
  .action(runCrossMode);

// Replay mode command
program
  .command('replay <caseName>')
  .description('Replay a previously discovered bug test case')
  .action(runReplayMode);

// 解析命令行参数
program.parse(process.argv);

// 如果没有提供任何命令，显示帮助信息
if (!process.argv.slice(2).length) {
  program.outputHelp();
}

// 导出函数供其他模块使用
export { runSingleMode, runCrossMode, runReplayMode };
