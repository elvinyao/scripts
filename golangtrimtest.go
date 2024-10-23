package stringutils

import (
    "strings"
    "testing"
)

func TestTrimSpace(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected string
        desc     string
    }{
        {
            name:     "普通空格",
            input:    "  hello world  ",
            expected: "hello world",
            desc:     "能够trim首尾的普通空格",
        },
        {
            name:     "制表符和换行符",
            input:    "\t\nhello world\n\t",
            expected: "hello world",
            desc:     "能够trim首尾的制表符和换行符",
        },
        {
            name:     "中间的空格",
            input:    "hello   world",
            expected: "hello   world",
            desc:     "不会trim中间的空格",
        },
        {
            name:     "全空格字符串",
            input:    "   \t\n\r   ",
            expected: "",
            desc:     "全是空格类字符会被完全trim",
        },
        {
            name:     "Unicode空格",
            input:    "\u2000hello\u2000",
            expected: "hello",
            desc:     "能够trim Unicode空格字符",
        },
        {
            name:     "空字符串",
            input:    "",
            expected: "",
            desc:     "空字符串保持不变",
        },
        {
            name:     "中文字符串带空格",
            input:    "  你好世界  ",
            expected: "你好世界",
            desc:     "能够trim中文字符串的空格",
        },
        {
            name:     "特殊字符",
            input:    "  !@#$%  ",
            expected: "!@#$%",
            desc:     "特殊字符保持不变，只trim空格",
        },
        {
            name:     "不可见字符组合",
            input:    "\u200B\u0020\u3000hello\u200B\u0020\u3000",
            expected: "hello",
            desc:     "能够trim零宽空格等不可见字符",
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := strings.TrimSpace(tt.input)
            if got != tt.expected {
                t.Errorf("TrimSpace() = %q, want %q\n描述: %s", got, tt.expected, tt.desc)
            }
        })
    }
}