// 测试调试系统的脚本
import { run } from './compiler-testing/cmd/src/runner.js';

// 设置环境变量来启用调试
process.env.DEBUG_LEVEL = 'DEBUG';

console.log('=== 测试调试系统 ===');
console.log('DEBUG_LEVEL:', process.env.DEBUG_LEVEL);

// 模拟运行测试
const testRun = async () => {
  try {
    console.log('\n1. 测试INFO级别日志:');
    // 这里会调用debugLog('INFO', ...)
    
    console.log('\n2. 测试DEBUG级别日志:');
    // 设置DEBUG级别后，应该能看到DEBUG日志
    
    console.log('\n3. 运行测试（模拟）:');
    // 注意：实际运行需要正确的config和mode参数
