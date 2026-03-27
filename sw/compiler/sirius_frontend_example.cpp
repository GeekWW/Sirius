//
// Sirius GPGPU - LLVM Frontend Example
// LLVM 前端示例：将简单的向量加法编译到Sirius ISA
//

#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Verifier.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

int main() {
    LLVMContext Context;
    Module *M = new Module("sirius_vector_add", Context);
    IRBuilder<> Builder(Context);

    // 创建函数：void vector_add(int* a, int* b, int* c, int n)
    FunctionType *FuncType = FunctionType::get(
        Type::getVoidTy(Context),
        {
            PointerType::get(Type::getInt32Ty(Context), 0),
            PointerType::get(Type::getInt32Ty(Context), 0),
            PointerType::get(Type::getInt32Ty(Context), 0),
            Type::getInt32Ty(Context)
        },
        false
    );

    Function *Func = Function::Create(
        FuncType,
        Function::ExternalLinkage,
        "vector_add",
        M
    );

    // 设置参数名称
    Function::arg_iterator Args = Func->arg_begin();
    Value *A = Args++;
    A->setName("a");
    Value *B = Args++;
    B->setName("b");
    Value *C = Args++;
    C->setName("c");
    Value *N = Args++;
    N->setName("n");

    // 创建入口块
    BasicBlock *EntryBB = BasicBlock::Create(Context, "entry", Func);
    Builder.SetInsertPoint(EntryBB);

    // 创建循环计数器
    Value *Zero = ConstantInt::get(Type::getInt32Ty(Context), 0);
    Value *One = ConstantInt::get(Type::getInt32Ty(Context), 1);

    // 循环初始化块
    BasicBlock *LoopInitBB = BasicBlock::Create(Context, "loop_init", Func);
    Builder.CreateBr(LoopInitBB);
    Builder.SetInsertPoint(LoopInitBB);

    // i = 0
    Value *I = Builder.CreateAlloca(Type::getInt32Ty(Context), nullptr, "i");
    Builder.CreateStore(Zero, I);

    // 循环条件块
    BasicBlock *LoopCondBB = BasicBlock::Create(Context, "loop_cond", Func);
    Builder.CreateBr(LoopCondBB);
    Builder.SetInsertPoint(LoopCondBB);

    // i < n ?
    Value *IVal = Builder.CreateLoad(Type::getInt32Ty(Context), I, "i.val");
    Value *Cond = Builder.CreateICmpSLT(IVal, N, "loop.cond");

    // 循环体块
    BasicBlock *LoopBodyBB = BasicBlock::Create(Context, "loop_body", Func);
    BasicBlock *LoopEndBB = BasicBlock::Create(Context, "loop_end", Func);
    Builder.CreateCondBr(Cond, LoopBodyBB, LoopEndBB);

    // 循环体
    Builder.SetInsertPoint(LoopBodyBB);

    // a[i]
    Value *AIdx = Builder.CreateGEP(Type::getInt32Ty(Context), A, IVal, "a.idx");
    Value *AVal = Builder.CreateLoad(Type::getInt32Ty(Context), AIdx, "a.val");

    // b[i]
    Value *BIdx = Builder.CreateGEP(Type::getInt32Ty(Context), B, IVal, "b.idx");
    Value *BVal = Builder.CreateLoad(Type::getInt32Ty(Context), BIdx, "b.val");

    // a[i] + b[i]
    Value *Sum = Builder.CreateAdd(AVal, BVal, "sum");

    // c[i] = sum
    Value *CIdx = Builder.CreateGEP(Type::getInt32Ty(Context), C, IVal, "c.idx");
    Builder.CreateStore(Sum, CIdx);

    // i++
    Value *INext = Builder.CreateAdd(IVal, One, "i.next");
    Builder.CreateStore(INext, I);

    // 回到循环条件
    Builder.CreateBr(LoopCondBB);

    // 循环结束
    Builder.SetInsertPoint(LoopEndBB);
    Builder.CreateRetVoid();

    // 验证模块
    verifyModule(*M, &errs());

    // 输出LLVM IR
    outs() << "Generated LLVM IR:\n";
    M->print(outs(), nullptr);

    // 这里可以添加代码来调用Sirius LLVM后端
    // 将LLVM IR编译到Sirius ISA

    delete M;
    return 0;
}

// 编译命令：
// clang++ -std=c++17 sirius_frontend_example.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core irreader support` -o sirius_frontend_example