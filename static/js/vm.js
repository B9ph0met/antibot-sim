
const OP = {"CONST":1,"ADD":2,"STORE":3,"LOAD":4,"HALT":5,"GET_GLOBAL":6,"GET_PROP":7,"EQ":8,"NOT":9,"JUMP_IF_FALSE":10,"JUMP":11,"SUB":12,"GT":13,"LT":14,"MUL":15,"XOR":16,"MOD":17,"BAND":18,"AND":19,"OR":20};

function run(bytecode, constants) {
    const stack = [];
    const variables = [];
    let pc = 0;
    
    while (true) {
        const op = bytecode[pc++];
        switch (op) {
            case OP.CONST:
                stack.push(constants[bytecode[pc++]]);
                break;
            case OP.ADD:
                const a = stack.pop();
                const b = stack.pop();
                stack.push(a + b);
                break;
            case OP.STORE:
                variables[bytecode[pc++]] = stack.pop();
                break;
            case OP.LOAD:
                stack.push(variables[bytecode[pc++]]);
                break;
            case OP.HALT:
                return variables;
            case OP.GET_GLOBAL:
                const name = constants[bytecode[pc++]]
                stack.push(window[name])
                break
            case OP.GET_PROP:
                const prop = constants[bytecode[pc++]]
                const obj = stack.pop()
                stack.push(obj[prop])
                break
            case OP.EQ:
                const eq_b = stack.pop()
                const eq_a = stack.pop()
                stack.push(eq_a === eq_b)
                break
            case OP.NOT:
                stack.push(!stack.pop())
                break
            case OP.JUMP_IF_FALSE:
                const jumpAddr = bytecode[pc++]
                if (!stack.pop()) {
                    pc = jumpAddr
                }
                break
            case OP.JUMP:
                pc = bytecode[pc]
                break
            case OP.SUB:
                const sub_b = stack.pop()
                const sub_a = stack.pop()
                stack.push(sub_a - sub_b)
                break
            case OP.GT:
                const gt_b = stack.pop();
                const gt_a = stack.pop();
                stack.push(gt_a > gt_b);
                break;
            case OP.LT:
                const lt_b = stack.pop();
                const lt_a = stack.pop();
                stack.push(lt_a < lt_b);
                break;
            case OP.MUL:
                const mul_b = stack.pop()
                const mul_a = stack.pop()
                stack.push(mul_a * mul_b)
                break
            case OP.XOR:
                const xor_b = stack.pop()
                const xor_a = stack.pop()
                stack.push(xor_a ^ xor_b)
                break
            case OP.MOD:
                const mod_b = stack.pop()
                const mod_a = stack.pop()
                stack.push(mod_a % mod_b)
                break
            case OP.BAND:
                const band_b = stack.pop()
                const band_a = stack.pop()
                stack.push(band_a & band_b)
                break
            case OP.AND:
                const and_b = stack.pop()
                const and_a = stack.pop()
                stack.push(and_a && and_b)
                break
            case OP.OR:
                const or_b = stack.pop()
                const or_a = stack.pop()
                stack.push(or_a || or_b)
                break
        }
    }
}

const BYTECODE = [1,0,3,0,6,1,7,2,1,3,8,3,1,6,4,7,5,7,6,3,2,6,7,7,8,7,9,3,3,6,10,7,11,3,4,6,12,7,13,3,5,4,1,10,52,4,0,1,14,2,3,0,4,2,1,15,8,10,66,4,0,1,16,2,3,0,4,2,1,17,14,10,80,4,0,1,18,2,3,0,4,3,1,19,8,10,94,4,0,1,20,2,3,0,4,0,1,21,15,4,4,1,22,15,2,4,5,1,23,15,2,4,2,1,24,15,2,3,6,4,6,1,25,16,3,6,4,6,1,26,17,3,6,5];
const CONSTANTS = [0,"navigator","webdriver",true,"navigator","plugins","length","navigator","languages","length","screen","width","screen","height",100,0,30,3,10,0,20,7919,31,17,13,48879313,1000000];
window.VM_RESULT = run(BYTECODE, CONSTANTS);
