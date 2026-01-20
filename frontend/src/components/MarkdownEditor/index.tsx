import { useState } from 'react';
import { Tabs } from 'antd';
import { Editor } from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';

interface MarkdownEditorProps {
  value?: string;
  onChange?: (value: string) => void;
  height?: string;
}

export default function MarkdownEditor({
  value = '',
  onChange,
  height = '500px',
}: MarkdownEditorProps) {
  const [activeTab, setActiveTab] = useState('edit');

  const handleEditorChange = (value: string | undefined) => {
    onChange?.(value || '');
  };

  return (
    <Tabs
      activeKey={activeTab}
      onChange={setActiveTab}
      items={[
        {
          key: 'edit',
          label: '编辑',
          children: (
            <Editor
              height={height}
              defaultLanguage="markdown"
              value={value}
              onChange={handleEditorChange}
              theme="vs-light"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                wordWrap: 'on',
              }}
            />
          ),
        },
        {
          key: 'preview',
          label: '预览',
          children: (
            <div
              className="prose max-w-none bg-gray-50 p-4 rounded overflow-auto"
              style={{ height }}
            >
              <ReactMarkdown>{value}</ReactMarkdown>
            </div>
          ),
        },
        {
          key: 'split',
          label: '分屏',
          children: (
            <div className="flex gap-4" style={{ height }}>
              <div className="flex-1">
                <Editor
                  height="100%"
                  defaultLanguage="markdown"
                  value={value}
                  onChange={handleEditorChange}
                  theme="vs-light"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    wordWrap: 'on',
                  }}
                />
              </div>
              <div className="flex-1 prose max-w-none bg-gray-50 p-4 rounded overflow-auto">
                <ReactMarkdown>{value}</ReactMarkdown>
              </div>
            </div>
          ),
        },
      ]}
    />
  );
}
