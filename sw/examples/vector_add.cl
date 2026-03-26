/*
 * Sirius GPGPU - Vector Addition Example
 * 向量加法示例
 */

__kernel void vector_add(__global const float* a,
                         __global const float* b,
                         __global float* c,
                         const unsigned int n) {
    unsigned int idx = get_global_id(0);
    
    if (idx < n) {
        c[idx] = a[idx] + b[idx];
    }
}
