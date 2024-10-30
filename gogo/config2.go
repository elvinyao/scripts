package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
    "path/filepath"
)

type Config struct {
    Username string `json:"username"`
}

func getDefaultConfigPath() (string, error) {
    // 获取用户的 AppData 目录
    configDir, err := os.UserConfigDir()
    if err != nil {
        return "", err
    }
    
    // 创建应用专属的配置目录
    appConfigDir := filepath.Join(configDir, "myapp")
    if err := os.MkdirAll(appConfigDir, 0755); err != nil {
        return "", err
    }
    
    // 返回完整的配置文件路径
    return filepath.Join(appConfigDir, "config.json"), nil
}

func loadConfig(path string) (*Config, error) {
    // 尝试读取配置文件
    file, err := os.Open(path)
    if err != nil {
        if os.IsNotExist(err) {
            return nil, nil // 文件不存在返回 nil
        }
        return nil, err
    }
    defer file.Close()

    var config Config
    if err := json.NewDecoder(file).Decode(&config); err != nil {
        return nil, err
    }

    return &config, nil
}

func saveConfig(config *Config, path string) error {
    // 创建或覆盖配置文件
    file, err := os.Create(path)
    if err != nil {
        return err
    }
    defer file.Close()

    // 将配置写入文件
    encoder := json.NewEncoder(file)
    encoder.SetIndent("", "    ")
    return encoder.Encode(config)
}

func promptUsername() string {
    reader := bufio.NewReader(os.Stdin)
    fmt.Print("请输入用户名: ")
    username, _ := reader.ReadString('\n')
    // 去除输入中的换行符
    return string([]byte(username)[:len(username)-1])
}

func main() {
    // 获取配置文件路径
    configPath, err := getDefaultConfigPath()
    if err != nil {
        fmt.Printf("获取配置路径失败: %v\n", err)
        return
    }

    // 加载配置
    config, err := loadConfig(configPath)
    if err != nil {
        fmt.Printf("加载配置失败: %v\n", err)
        return
    }

    // 如果配置不存在，创建新配置
    if config == nil {
        username := promptUsername()
        config = &Config{
            Username: username,
        }
        
        // 保存新配置
        if err := saveConfig(config, configPath); err != nil {
            fmt.Printf("保存配置失败: %v\n", err)
            return
        }
        fmt.Println("配置已保存")
    }

    // 显示当前配置
    fmt.Printf("当前用户名: %s\n", config.Username)
}