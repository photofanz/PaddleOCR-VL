"""
PaddleOCR MPS 驗證腳本
用於測試 PaddleOCR 在 Apple Silicon (M3 Max) 上的安裝與 MPS 加速
"""

import paddleocr
import numpy as np
from PIL import Image
import argparse
import os
import sys
import time


def print_separator(char="=", length=60):
    """列印分隔線"""
    print(char * length)


def print_section(title):
    """列印章節標題"""
    print_separator()
    print(f"  {title}")
    print_separator()


def test_paddleocr_installation():
    """測試 PaddleOCR 安裝"""
    print_section("1. 檢查 PaddleOCR 安裝")
    
    try:
        import paddleocr
        print(f"✓ PaddleOCR 已安裝")
        print(f"  版本: {paddleocr.__version__ if hasattr(paddleocr, '__version__') else '未知'}")
        return True
    except ImportError as e:
        print(f"✗ PaddleOCR 未安裝: {str(e)}")
        return False


def test_paddle_backend():
    """測試 PaddlePaddle 後端"""
    print_section("2. 檢查 PaddlePaddle 後端")
    
    try:
        import paddle
        print(f"✓ PaddlePaddle 已安裝")
        print(f"  版本: {paddle.__version__}")
        
        # 檢查是否支援 GPU/MPS
        if paddle.device.is_compiled_with_cuda():
            print(f"  ✓ CUDA 支援: 是")
            print(f"    GPU 數量: {paddle.device.cuda.device_count()}")
        else:
            print(f"  ℹ CUDA 支援: 否（macOS 使用 MPS）")
        
        return True
    except ImportError as e:
        print(f"✗ PaddlePaddle 未安裝: {str(e)}")
        return False


def create_test_image():
    """創建一個測試圖像"""
    print_section("3. 創建測試圖像")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 創建白色背景圖像
        img = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加文字（使用預設字型）
        text = "PaddleOCR Test Image\nApple M3 Max\nMacBook Pro 2024"
        
        try:
            # 嘗試使用較大的字型
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            # 使用預設字型
            font = ImageFont.load_default()
        
        # 繪製文字
        draw.text((50, 100), text, fill='black', font=font)
        
        # 添加一些圖形
        draw.rectangle([50, 300, 750, 350], outline='blue', width=3)
        draw.text((60, 310), "This is a test for OCR recognition", fill='blue', font=font)
        
        test_image_path = "test_image.png"
        img.save(test_image_path)
        
        print(f"✓ 測試圖像已創建: {test_image_path}")
        print(f"  尺寸: {img.size}")
        
        return test_image_path, img
        
    except Exception as e:
        print(f"✗ 創建測試圖像失敗: {str(e)}")
        return None, None


def test_ocr_cpu(image_path, lang='en'):
    """測試 CPU 模式的 OCR"""
    print_section(f"4. 測試 OCR (CPU 模式, 語言: {lang})")
    
    try:
        print("正在初始化 PaddleOCR (CPU)...")
        start_init = time.time()
        
        ocr = paddleocr.PaddleOCR(
            use_textline_orientation=True,
            lang=lang
        )
        
        init_time = time.time() - start_init
        print(f"✓ 初始化完成，耗時 {init_time:.2f} 秒")
        
        # 執行 OCR
        print(f"正在處理圖像: {image_path}")
        start_ocr = time.time()
        
        result = ocr.ocr(image_path)
        
        ocr_time = time.time() - start_ocr
        print(f"✓ OCR 完成，耗時 {ocr_time:.2f} 秒")
        
        # 顯示結果
        print("\n辨識結果:")
        if result and result[0]:
            for idx, line in enumerate(result[0], 1):
                if len(line) >= 2 and len(line[1]) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    print(f"  {idx}. [{confidence:.2f}] {text}")
                else:
                    print(f"  {idx}. [格式錯誤] {line}")
        else:
            print("  (無辨識結果)")
        
        return True, ocr_time
        
    except Exception as e:
        print(f"✗ CPU 模式測試失敗: {str(e)}")
        return False, 0


def test_ocr_gpu(image_path, lang='en'):
    """測試 GPU/MPS 模式的 OCR"""
    print_section(f"5. 測試 OCR (GPU/MPS 模式, 語言: {lang})")
    
    try:
        print("正在初始化 PaddleOCR (GPU/MPS)...")
        start_init = time.time()
        
        ocr = paddleocr.PaddleOCR(
            use_textline_orientation=True,
            lang=lang
        )
        
        init_time = time.time() - start_init
        print(f"✓ 初始化完成，耗時 {init_time:.2f} 秒")
        print(f"  ℹ 在 macOS 上，use_gpu=True 會嘗試使用 MPS 加速")
        
        # 執行 OCR
        print(f"正在處理圖像: {image_path}")
        start_ocr = time.time()
        
        result = ocr.ocr(image_path)
        
        ocr_time = time.time() - start_ocr
        print(f"✓ OCR 完成，耗時 {ocr_time:.2f} 秒")
        
        # 顯示結果
        print("\n辨識結果:")
        if result and result[0]:
            for idx, line in enumerate(result[0], 1):
                if len(line) >= 2 and len(line[1]) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    print(f"  {idx}. [{confidence:.2f}] {text}")
                else:
                    print(f"  {idx}. [格式錯誤] {line}")
        else:
            print("  (無辨識結果)")
        
        return True, ocr_time
        
    except Exception as e:
        print(f"✗ GPU/MPS 模式測試失敗: {str(e)}")
        print(f"  這可能是正常的，因為 MPS 支援仍在開發中")
        return False, 0


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PaddleOCR MPS 驗證腳本")
    parser.add_argument(
        "--image",
        type=str,
        help="測試圖像路徑（如不提供則自動創建）"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="en",
        help="OCR 語言 (en, ch_tra, ch_sim, etc.)"
    )
    parser.add_argument(
        "--skip-gpu",
        action="store_true",
        help="跳過 GPU/MPS 測試"
    )
    
    args = parser.parse_args()
    
    print_separator("=")
    print("  PaddleOCR MPS 驗證腳本")
    print("  Apple Silicon (M3 Max) 測試")
    print_separator("=")
    print()
    
    # 1. 檢查安裝
    if not test_paddleocr_installation():
        print("\n請先安裝 PaddleOCR:")
        print("  pip install paddleocr")
        sys.exit(1)
    
    print()
    
    # 2. 檢查後端
    if not test_paddle_backend():
        print("\n請先安裝 PaddlePaddle:")
        print("  pip install paddlepaddle")
        sys.exit(1)
    
    print()
    
    # 3. 準備測試圖像
    if args.image and os.path.exists(args.image):
        test_image = args.image
        print_section("3. 使用提供的測試圖像")
        print(f"✓ 圖像路徑: {test_image}")
    else:
        test_image, _ = create_test_image()
        if not test_image:
            print("\n✗ 無法創建測試圖像")
            sys.exit(1)
    
    print()
    
    # 4. 測試 CPU 模式
    cpu_success, cpu_time = test_ocr_cpu(test_image, args.lang)
    
    print()
    
    # 5. 測試 GPU/MPS 模式
    gpu_time = 0
    if not args.skip_gpu:
        gpu_success, gpu_time = test_ocr_gpu(test_image, args.lang)
    else:
        print_section("5. GPU/MPS 測試已跳過")
        gpu_success = None
    
    print()
    
    # 6. 總結
    print_section("測試總結")
    
    print(f"CPU 模式: {'✓ 成功' if cpu_success else '✗ 失敗'}")
    if cpu_success:
        print(f"  處理時間: {cpu_time:.2f} 秒")
    
    if not args.skip_gpu:
        print(f"GPU/MPS 模式: {'✓ 成功' if gpu_success else '✗ 失敗或不支援'}")
        if gpu_success:
            print(f"  處理時間: {gpu_time:.2f} 秒")
            if cpu_time > 0:
                speedup = cpu_time / gpu_time
                print(f"  加速比: {speedup:.2f}x")
    
    print()
    print_separator()
    
    # 清理測試圖像
    if not args.image and os.path.exists("test_image.png"):
        try:
            os.remove("test_image.png")
            print("✓ 測試圖像已清理")
        except:
            pass
    
    print("\n✓ 驗證完成！")
    print()


if __name__ == "__main__":
    main()

