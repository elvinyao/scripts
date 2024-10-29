package main

import (
    "fmt"
    "os"
    "os/signal"
    "syscall"
    
    "github.com/eiannone/keyboard"
)

func main() {
    // 初始化键盘监听
    if err := keyboard.Open(); err != nil {
        fmt.Println("无法初始化键盘:", err)
        os.Exit(1)
    }
    defer keyboard.Close()

    // 设置信号处理
    signalChan := make(chan os.Signal, 1)
    signal.Notify(signalChan, syscall.SIGINT, syscall.SIGTERM)

    fmt.Println("程序已启动，按ESC键退出...")

    // 创建一个用于接收键盘事件的channel
    keyChan := make(chan keyboard.Key)
    
    // 在goroutine中监听键盘输入
    go func() {
        for {
            char, key, err := keyboard.GetKey()
            if err != nil {
                fmt.Println("键盘读取错误:", err)
                os.Exit(1)
            }
            if key == keyboard.KeyEsc {
                keyChan <- key
                return
            }
            fmt.Printf("你按下了: %q  key: %v\n", char, key)
        }
    }()

    // 等待ESC键或系统信号
    select {
    case <-keyChan:
        fmt.Println("\n检测到ESC键，正在退出程序...")
    case sig := <-signalChan:
        fmt.Printf("\n收到系统信号 %v，正在退出程序...\n", sig)
    }
}