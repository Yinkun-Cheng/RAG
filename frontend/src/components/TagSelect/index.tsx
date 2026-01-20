import { useState } from 'react';
import { Select, Tag, Input, Button, Space, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { SelectProps } from 'antd';

interface TagSelectProps {
  value?: string[];
  onChange?: (value: string[]) => void;
  availableTags: { id: string; name: string; color: string }[];
}

export default function TagSelect({ value = [], onChange, availableTags }: TagSelectProps) {
  const [inputVisible, setInputVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const handleChange = (newValue: string[]) => {
    onChange?.(newValue);
  };

  const handleInputConfirm = () => {
    if (inputValue && !availableTags.find(tag => tag.name === inputValue)) {
      message.success(`新建标签"${inputValue}"成功`);
      // 这里应该调用 API 创建新标签
      setInputValue('');
      setInputVisible(false);
    } else if (inputValue) {
      message.warning('标签已存在');
    }
  };

  const tagRender: SelectProps['tagRender'] = props => {
    const { label, closable, onClose } = props;
    const tag = availableTags.find(t => t.name === label);
    const color = tag?.color || 'default';

    return (
      <Tag color={color} closable={closable} onClose={onClose} style={{ marginRight: 3 }}>
        {label}
      </Tag>
    );
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Select
        mode="multiple"
        style={{ width: '100%' }}
        placeholder="选择标签"
        value={value}
        onChange={handleChange}
        tagRender={tagRender}
        options={availableTags.map(tag => ({
          label: tag.name,
          value: tag.name,
        }))}
      />
      {inputVisible ? (
        <Input
          type="text"
          size="small"
          style={{ width: 200 }}
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onBlur={handleInputConfirm}
          onPressEnter={handleInputConfirm}
          placeholder="输入新标签名称"
          autoFocus
        />
      ) : (
        <Button
          size="small"
          type="dashed"
          icon={<PlusOutlined />}
          onClick={() => setInputVisible(true)}
        >
          新建标签
        </Button>
      )}
    </Space>
  );
}
