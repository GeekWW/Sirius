/*
 * Sirius GPGPU - Matrix Multiplication Example
 * 矩阵乘法示例
 */

#define TILE_SIZE 16

__kernel void matrix_mult(__global const float* A,
                          __global const float* B,
                          __global float* C,
                          const unsigned int N) {
    unsigned int row = get_global_id(1);
    unsigned int col = get_global_id(0);
    
    if (row < N && col < N) {
        float sum = 0.0f;
        
        for (unsigned int k = 0; k < N; k++) {
            sum += A[row * N + k] * B[k * N + col];
        }
        
        C[row * N + col] = sum;
    }
}
