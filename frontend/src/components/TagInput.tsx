import React, { useState, useRef, useEffect } from 'react';

interface Tag {
  id: string;
  text: string;
}

interface TagInputProps {
  tags: Tag[];
  onAddTag: (tag: Tag) => void;
  onRemoveTag: (tagId: string) => void;
  placeholder?: string;
  maxTags?: number;
  className?: string;
}

export const TagInput: React.FC<TagInputProps> = ({
  tags,
  onAddTag,
  onRemoveTag,
  placeholder = 'Agregar etiqueta...',
  maxTags = 10,
  className = '',
}) => {
  const [input, setInput] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isComposing && input.trim()) {
      e.preventDefault();
      if (tags.length >= maxTags) {
        return;
      }
      const newTag: Tag = {
        id: Date.now().toString(),
        text: input.trim(),
      };
      onAddTag(newTag);
      setInput('');
    } else if (e.key === 'Backspace' && !input && tags.length > 0) {
      onRemoveTag(tags[tags.length - 1].id);
    }
  };

  const handleRemoveTag = (tagId: string) => {
    onRemoveTag(tagId);
  };

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  return (
    <div
      className={`flex flex-wrap gap-2 p-2 border border-gray-300 rounded-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 ${className}`}
    >
      {tags.map((tag) => (
        <span
          key={tag.id}
          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
        >
          {tag.text}
          <button
            type="button"
            onClick={() => handleRemoveTag(tag.id)}
            className="flex-shrink-0 ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center text-blue-400 hover:bg-blue-200 hover:text-blue-500 focus:outline-none focus:bg-blue-500 focus:text-white"
          >
            <span className="sr-only">Eliminar etiqueta</span>
            <svg
              className="h-2 w-2"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 8 8"
            >
              <path
                strokeLinecap="round"
                strokeWidth="1.5"
                d="M1 1l6 6m0-6L1 7"
              />
            </svg>
          </button>
        </span>
      ))}
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onCompositionStart={() => setIsComposing(true)}
        onCompositionEnd={() => setIsComposing(false)}
        placeholder={tags.length >= maxTags ? 'Límite alcanzado' : placeholder}
        disabled={tags.length >= maxTags}
        className="flex-1 outline-none bg-transparent text-sm min-w-[120px]"
      />
    </div>
  );
};
