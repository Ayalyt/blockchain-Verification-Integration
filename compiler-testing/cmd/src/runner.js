import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 简单调试输出函数
function debugLog(message, data = null) {
  const timestamp = `[${new Date().toISOString()}]`;
  const memUsage = `[Memory: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB]`;
  
  console.log(`${timestamp}${memUsage} ${message}`);
  
  if (data) {
    console.log('调试数据:', typeof data === 'object' ? JSON.stringify(data, null, 2) : data);
  }
}

const getConfigNameByVersion = (version) => {
  console.log(`[调试] 获取版本 ${version} 的配置名称`);
  if (version === '2.1.8') {
    return 'config-default-1';
  }
  return 'config-default-2';
};

function getLast10Lines(text) {
  const lines = text.trim().split('\n');
  console.log(`[调试] 从输出中提取最后10行，总行数: ${lines.length}`);
  return lines.slice(-10);
}

function extractTBCCTFIWValue(lines) {
  const regex = /<<<tbcctfiw>>>(.*?)<<<\/tbcctfiw>>>/;
  console.log(`[调试] 在 ${lines.length} 行中搜索 tbcctfiw 模式`);
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const match = line.match(regex);
    if (match) {
      console.log(`[调试] 在第 ${i} 行找到 tbcctfiw 值: ${match[1].trim()}`);
      return match[1].trim();
    }
  }
  
  console.log('[调试] 在输出中未找到 tbcctfiw 模式');
  return null;
}

function runScript(config, mode) {
  return new Promise((resolve) => {
    const scriptPath = path.resolve(__dirname, './shell/run.sh');
    console.log(`\n[调试] 开始执行脚本:`);
    console.log(`  脚本路径: ${scriptPath}`);
    console.log(`  配置: ${config}`);
    console.log(`  模式: ${mode}`);
    console.log(`  超时: 120000ms`);

    const child = spawn(scriptPath, [config, mode], {
      shell: true,
      timeout: 120000
    });

    let outputBuffer = [];
    let errorBuffer = [];
    const startTime = Date.now();

    child.stdout.on('data', (data) => {
      const text = data.toString();
      outputBuffer.push(text);
      console.log(`[STDOUT] ${text.trim().substring(0, 200)}${text.length > 200 ? '...' : ''}`);
    });

    child.stderr.on('data', (data) => {
      const text = data.toString();
      errorBuffer.push(text);
      console.log(`[STDERR] ${text.trim().substring(0, 200)}${text.length > 200 ? '...' : ''}`);
    });

    child.on('close', (code, signal) => {
      const executionTime = Date.now() - startTime;
      const fullOutput = outputBuffer.join('');
      const fullError = errorBuffer.join('');
      const last10Lines = getLast10Lines(fullOutput);
      const tbcctfiwValue = extractTBCCTFIWValue(last10Lines);

      console.log(`\n[调试] 脚本执行完成:`);
      console.log(`  退出码: ${code}`);
      console.log(`  信号: ${signal}`);
      console.log(`  执行时间: ${executionTime}ms`);
      console.log(`  输出长度: ${fullOutput.length} 字符`);
      console.log(`  错误长度: ${fullError.length} 字符`);
      console.log(`  tbcctfiw值: ${tbcctfiwValue || '未找到'}`);

      if (tbcctfiwValue && tbcctfiwValue !== '0') {
        console.log('\n' + '='.repeat(80));
        console.log('!!! 发现BUG !!!');
        console.log('='.repeat(80));
        console.log(`tbcctfiw值: ${tbcctfiwValue}`);
        console.log('\n---- 完整输出 (前2000字符) ----');
        console.log(fullOutput.substring(0, 2000) + (fullOutput.length > 2000 ? '...' : ''));
        if (fullError) {
          console.log('\n---- 完整错误输出 ----');
          console.log(fullError);
        }
        console.log('='.repeat(80) + '\n');
      } else if (fullError) {
        console.log('\n' + '-'.repeat(80));
        console.log('警告: 脚本有错误输出');
        console.log('-'.repeat(80));
        console.log(fullError);
        console.log('-'.repeat(80) + '\n');
      }

      resolve(!!(tbcctfiwValue && tbcctfiwValue !== '0'));
    });

    child.on('error', (err) => {
      const executionTime = Date.now() - startTime;
      console.log(`\n[调试] 脚本执行失败:`);
      console.log(`  错误: ${err.message}`);
      console.log(`  执行时间: ${executionTime}ms`);
      resolve(false);
    });
  });
}

const copyCircomFileAndShow = (version) => {
  console.log(`\n[调试] 复制并显示版本 ${version} 的circom文件`);
  
  try {
    const configFile = path.resolve(
      __dirname,
      `../../config/${getConfigNameByVersion(version)}.json`
    );
    console.log(`[调试] 读取配置文件: ${configFile}`);
    
    const configInfo = JSON.parse(fs.readFileSync(configFile, 'utf8'));
    console.log(`[调试] 配置加载成功:`);
    console.log(`  临时文件夹: ${configInfo.temp_folder}`);
    console.log(`  结果文件夹: ${configInfo.result_folder}`);
    
    const tempFolder = configInfo.temp_folder;
    const circomFile1 = path.resolve(tempFolder, 'temp1.circom');
    const circomFile2 = path.resolve(tempFolder, 'temp2.circom');
    
    console.log(`[调试] 检查circom文件是否存在:`);
    console.log(`  文件1: ${circomFile1} - ${fs.existsSync(circomFile1) ? '存在' : '不存在'}`);
    console.log(`  文件2: ${circomFile2} - ${fs.existsSync(circomFile2) ? '存在' : '不存在'}`);
    
    if (fs.existsSync(circomFile1)) {
      const content1 = fs.readFileSync(circomFile1, 'utf8');
      console.log('\n' + '='.repeat(80));
      console.log('调试: CIRCOM 文件 #1 (发现BUG)');
      console.log('='.repeat(80));
      console.log(`文件: ${circomFile1}`);
      console.log(`大小: ${content1.length} 字符`);
      console.log('='.repeat(80));
      console.log(content1);
      console.log('='.repeat(80) + '\n');
    } else {
      console.log(`[调试] Circom文件 #1 未找到: ${circomFile1}`);
    }
    
    if (fs.existsSync(circomFile2)) {
      const content2 = fs.readFileSync(circomFile2, 'utf8');
      console.log('\n' + '='.repeat(80));
      console.log('调试: CIRCOM 文件 #2 (发现BUG)');
      console.log('='.repeat(80));
      console.log(`文件: ${circomFile2}`);
      console.log(`大小: ${content2.length} 字符`);
      console.log('='.repeat(80));
      console.log(content2);
      console.log('='.repeat(80) + '\n');
    } else {
      console.log(`[调试] Circom文件 #2 未找到: ${circomFile2}`);
    }
    
    const resultFolder = configInfo.result_folder;
    if (fs.existsSync(circomFile1)) {
      fs.copyFileSync(circomFile1, path.resolve(resultFolder, '1.circom'));
      console.log(`[调试] 已复制 ${circomFile1} 到 ${path.resolve(resultFolder, '1.circom')}`);
    }
    if (fs.existsSync(circomFile2)) {
      fs.copyFileSync(circomFile2, path.resolve(resultFolder, '2.circom'));
      console.log(`[调试] 已复制 ${circomFile2} 到 ${path.resolve(resultFolder, '2.circom')}`);
    }
    
  } catch (error) {
    console.log(`[调试] copyCircomFileAndShow 错误:`);
    console.log(`  错误: ${error.message}`);
    console.log(`  堆栈: ${error.stack}`);
    console.log(`  版本: ${version}`);
  }
};

const showCoverageByVersion = (version) => {
  console.log(`\n[调试] 显示版本 ${version} 的覆盖率`);
  
  try {
    const configFile = path.resolve(
      __dirname,
      `../../config/${getConfigNameByVersion(version)}.json`
    );
    const configInfo = JSON.parse(fs.readFileSync(configFile, 'utf8'));
    
    const coverageFilePath = path.resolve(configInfo.coverage_folder, 'html/coverage.json');
    console.log(`[调试] 读取覆盖率文件: ${coverageFilePath}`);
    
    if (!fs.existsSync(coverageFilePath)) {
      console.log(`[调试] 覆盖率文件未找到: ${coverageFilePath}`);
      console.log(`版本: ${version} 覆盖率: 文件未找到`);
      return;
    }
    
    const coverage = JSON.parse(fs.readFileSync(coverageFilePath, 'utf8'));
    
    console.log('\n' + '-'.repeat(60));
    console.log('覆盖率报告');
    console.log('-'.repeat(60));
    console.log(`版本: ${version}`);
    console.log(`消息: ${coverage.message}`);
    
    if (coverage.total && coverage.covered) {
      const percentage = (coverage.covered / coverage.total * 100).toFixed(2);
      console.log(`覆盖率: ${coverage.covered}/${coverage.total} (${percentage}%)`);
    }
    
    if (coverage.branches) {
      console.log(`分支: ${JSON.stringify(coverage.branches)}`);
    }
    
    console.log('-'.repeat(60) + '\n');
    
    console.log(`[调试] 已显示版本 ${version} 的覆盖率: ${coverage.message}`);
    
  } catch (error) {
    console.log(`[调试] 显示版本 ${version} 覆盖率时出错:`);
    console.log(`  错误: ${error.message}`);
    console.log(`  堆栈: ${error.stack}`);
    console.log(`版本: ${version} 覆盖率: 错误 - ${error.message}`);
  }
};

export const run = async (config, mode, addtionalInfo) => {
  console.log('\n' + '='.repeat(80));
  console.log('测试运行器启动');
  console.log('='.repeat(80));
  console.log(`开始时间: ${new Date().toISOString()}`);
  console.log(`最大迭代次数: 2000`);
  console.log(`配置: ${config}`);
  console.log(`模式: ${mode}`);
  if (addtionalInfo) {
    console.log(`附加信息: ${JSON.stringify(addtionalInfo, null, 2)}`);
  }
  console.log('='.repeat(80) + '\n');
  
  let count = 0;
  const timeStart = Date.now();
  const MAX_ITERATIONS = 2000;
  let lastBugFoundTime = null;
  let totalExecutionTime = 0;
  
  while (count < MAX_ITERATIONS) {
    const iterationStart = Date.now();
    try {
      count++;
      
      console.log(`\n[调试] 开始第 ${count}/${MAX_ITERATIONS} 次迭代`);
      console.log(`  已用时间: ${Math.floor((Date.now() - timeStart) / 1000)}秒`);
      console.log(`  内存使用: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`);
      
      if (count === 1) {
        console.log(`\n>>> 第 ${count} 次运行`);
      } else {
        const elapsed = Math.floor((Date.now() - timeStart) / 1000);
        const avgTimePerIteration = totalExecutionTime > 0 ? 
          Math.round(totalExecutionTime / (count - 1)) : 0;
        const estimatedRemaining = avgTimePerIteration > 0 ? 
          Math.round((MAX_ITERATIONS - count) * avgTimePerIteration / 1000) : 0;
          
        console.log(
          `\n>>> 第 ${count} 次运行, 已用: ${elapsed}秒, ` +
          `平均: ${avgTimePerIteration}毫秒/次, ` +
          `预计剩余: ${estimatedRemaining}秒`
        );
      }
      
      const shouldStop = await runScript(config, mode);
      const iterationTime = Date.now() - iterationStart;
      totalExecutionTime += iterationTime;
      
      console.log(`[调试] 第 ${count} 次迭代完成`);
      console.log(`  迭代时间: ${iterationTime}毫秒`);
      console.log(`  是否停止: ${shouldStop}`);
      console.log(`  累计时间: ${totalExecutionTime}毫秒`);
      
      if (shouldStop) {
        lastBugFoundTime = Date.now();
        const totalElapsed = Math.floor((lastBugFoundTime - timeStart) / 1000);
        
        console.log('\n' + '='.repeat(80));
        console.log('!!! 发现BUG !!!');
        console.log('='.repeat(80));
        console.log(`迭代: ${count}/${MAX_ITERATIONS}`);
        console.log(`总时间: ${totalElapsed} 秒`);
        console.log(`平均每次迭代时间: ${Math.round(totalExecutionTime / count)}毫秒`);
        console.log(`BUG发现时间: ${new Date(lastBugFoundTime).toISOString()}`);
        console.log('='.repeat(80) + '\n');
        
        if (addtionalInfo?.versions?.length) {
          console.log(`[调试] 处理版本 ${addtionalInfo.versions.join(', ')} 的BUG详情`);
          console.log('\n' + '='.repeat(80));
          console.log('BUG详情');
          console.log('='.repeat(80));
          copyCircomFileAndShow(addtionalInfo.versions[0]);
        }
        
        console.log('\n' + '='.repeat(80));
        console.log('覆盖率报告汇总');
        console.log('='.repeat(80));
        if (addtionalInfo?.versions?.length) {
          addtionalInfo.versions.forEach(showCoverageByVersion);
        } else {
          console.log('未提供版本信息用于覆盖率报告');
        }
        console.log('='.repeat(80) + '\n');
        
        console.log(`[调试] 测试完成，发现BUG`);
        console.log(`  迭代次数: ${count}`);
        console.log(`  总时间: ${totalElapsed}秒`);
        console.log(`  BUG发现时间: ${new Date(lastBugFoundTime).toISOString()}`);
        
        break;
      }
      
      // 添加进度报告
      if (count % 100 === 0) {
        const progress = ((count / MAX_ITERATIONS) * 100).toFixed(1);
        const elapsed = Math.floor((Date.now() - timeStart) / 1000);
        console.log(`\n[进度] ${progress}% 完成 (${count}/${MAX_ITERATIONS})`);
        console.log(`  已用时间: ${elapsed}秒`);
        console.log(`  平均迭代时间: ${Math.round(totalExecutionTime / count)}毫秒`);
      }
      
      await new Promise((res) => setTimeout(res, 1000));
    } catch (e) {
      const iterationTime = Date.now() - iterationStart;
      console.log(`\n[错误] 第 ${count} 次迭代失败:`);
      console.log(`  错误: ${e.message}`);
      console.log(`  堆栈: ${e.stack}`);
      console.log(`  迭代时间: ${iterationTime}毫秒`);
    }
  }
  
  if (count >= MAX_ITERATIONS) {
    const totalElapsed = Math.floor((Date.now() - timeStart) / 1000);
    const avgIterationTime = Math.round(totalExecutionTime / MAX_ITERATIONS);
    
    console.log('\n' + '='.repeat(80));
    console.log('测试终止 - 达到最大迭代次数');
    console.log('='.repeat(80));
    console.log(`总迭代次数: ${MAX_ITERATIONS}`);
    console.log(`总时间: ${totalElapsed} 秒`);
    console.log(`平均每次迭代时间: ${avgIterationTime}毫秒`);
    console.log(`在 ${MAX_ITERATIONS} 次迭代中未发现BUG`);
    console.log('='.repeat(80) + '\n');
  }
  
  // 最终统计
  const finalStats = {
    totalIterations: count,
    maxIterations: MAX_ITERATIONS,
    totalExecutionTime: Math.floor((Date.now() - timeStart) / 1000) + '秒',
    bugFound: lastBugFoundTime !== null,
    bugFoundTime: lastBugFoundTime ? new Date(lastBugFoundTime).toISOString() : null,
    averageIterationTime: count > 0 ? Math.round(totalExecutionTime / count) + '毫秒' : 'N/A'
  };
  
  console.log(`[调试] 测试运行器完成`);
  console.log(`  最终统计: ${JSON.stringify(finalStats, null, 2)}`);
  
  console.log('\n' + '='.repeat(80));
  console.log('最终统计');
  console.log('='.repeat(80));
  console.log(JSON.stringify(finalStats, null, 2));
  console.log('='.repeat(80) + '\n');
  
  return finalStats.bugFound;
};
