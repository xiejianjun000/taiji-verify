#!/usr/bin/env python3
"""
Taiji Verify CLI - 命令行工具

使用方式:
    taiji-verify --text "待验证文本" --ground-truth "标准答案"
    taiji-verify --text "文本" --json  # JSON输出
    echo "文本" | taiji-verify --stdin
    taiji-verify --version

安装后自动可用:
    pip install taiji-verify
"""

import sys
import json
import argparse
from typing import Optional

from taiji_verify.plugin import verify, TaijiVerify


def format_result(result, json_output: bool = False) -> str:
    """格式化输出"""
    if json_output:
        return json.dumps({
            "verdict": result.verdict,
            "is_passing": result.is_passing,
            "delta_s": result.delta_s,
            "risk_level": result.risk_level,
            "failures": [
                {
                    "pattern": str(getattr(f, "pattern", "")),
                    "severity": str(getattr(f, "severity", "")),
                    "description": getattr(f, "description", ""),
                }
                for f in result.failures
            ],
            "processing_time_ms": result.processing_time_ms,
        }, ensure_ascii=False, indent=2)
    else:
        status = "✅ PASS" if result.is_passing else "❌ FAIL"
        delta_str = f"{result.delta_s:.4f}" if result.delta_s is not None else "N/A"
        output = [
            f"Taiji Verify",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"判定: {result.verdict.upper()}",
            f"状态: {status}",
            f"ΔS:   {delta_str}",
            f"风险: {result.risk_level or 'N/A'}",
            f"耗时: {result.processing_time_ms}ms",
        ]
        if result.failures:
            output.append(f"失败: {len(result.failures)} 个")
            for f in result.failures[:3]:
                output.append(f"  - {getattr(f, 'description', str(f))}")
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        prog="taiji-verify",
        description="Taiji Verify CLI - 太极验证引擎命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  taiji-verify --text "AI输出" --ground-truth "标准答案"
  taiji-verify --text "文本" --json
  echo "待验证文本" | taiji-verify --stdin
  taiji-verify --batch file.txt
  taiji-verify --version
        """,
    )

    parser.add_argument(
        "--text", "-t",
        type=str,
        help="待验证的文本",
    )

    parser.add_argument(
        "--ground-truth", "-g",
        type=str,
        help="标准答案/真值",
    )

    parser.add_argument(
        "--stdin", "-s",
        action="store_true",
        help="从stdin读取文本",
    )

    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="JSON格式输出",
    )

    parser.add_argument(
        "--batch", "-b",
        type=str,
        help="批量文件路径 (每行一个文本)",
    )

    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=768,
        help="向量维度 (默认768)",
    )

    parser.add_argument(
        "--delta-threshold",
        type=float,
        default=0.6,
        help="ΔS阈值 (默认0.6)",
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version="taiji-verify 2.0.0",
    )

    args = parser.parse_args()

    # 读取文本
    text: Optional[str] = None

    if args.stdin:
        text = sys.stdin.read().strip()
    elif args.text:
        text = args.text
    elif args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"错误: 文件不存在: {args.batch}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"错误: 读取文件失败: {e}", file=sys.stderr)
            sys.exit(1)

        verifier = TaijiVerify(
            embedding_dim=args.embedding_dim,
            delta_threshold=args.delta_threshold,
        )

        results = []
        for i, line in enumerate(lines):
            result = verifier.verify(line, args.ground_truth)
            result.line_num = i + 1
            results.append(result)

        if args.json:
            output = [
                {
                    "line": r.line_num,
                    "verdict": r.verdict,
                    "is_passing": r.is_passing,
                    "delta_s": r.delta_s,
                }
                for r in results
            ]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            passed = sum(1 for r in results if r.is_passing)
            print(f"批量验证: {passed}/{len(results)} 通过")
            for r in results:
                status = "✅" if r.is_passing else "❌"
                delta_str = f"{r.delta_s:.3f}" if r.delta_s is not None else "N/A"
                print(f"  {status} L{r.line_num}: {r.verdict} | ΔS={delta_str}")
        return

    if not text:
        parser.print_help()
        sys.exit(1)

    # 单条验证
    verifier = TaijiVerify(
        embedding_dim=args.embedding_dim,
        delta_threshold=args.delta_threshold,
    )

    result = verifier.verify(text, args.ground_truth)
    print(format_result(result, args.json))


if __name__ == "__main__":
    main()
