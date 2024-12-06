// Mock global FormData
global.FormData = class FormData {
  private _data: { [key: string]: any[] } = {};

  append(key: string, value: any) {
    if (!this._data[key]) {
      this._data[key] = [];
    }
    this._data[key].push(value);
  }

  get(key: string) {
    return this._data[key]?.[0];
  }

  getAll(key: string) {
    return this._data[key] || [];
  }

  delete(key: string) {
    delete this._data[key];
  }

  has(key: string) {
    return key in this._data;
  }

  set(key: string, value: any) {
    this._data[key] = [value];
  }

  forEach(callback: (value: any, key: string, parent: FormData) => void) {
    Object.keys(this._data).forEach(key => {
      this._data[key].forEach(value => {
        callback(value, key, this);
      });
    });
  }
} as any;

// Mock global File
global.File = class File extends Blob {
  name: string;
  lastModified: number;

  constructor(bits: BlobPart[], name: string, options?: FilePropertyBag) {
    super(bits, options);
    this.name = name;
    this.lastModified = options?.lastModified || Date.now();
  }

  arrayBuffer(): Promise<ArrayBuffer> {
    return Promise.resolve(new ArrayBuffer(this.size));
  }
} as any;

// Mock global Blob
global.Blob = class Blob {
  private _content: BlobPart[];
  size: number;
  type: string;

  constructor(bits: BlobPart[] = [], options?: BlobPropertyBag) {
    this._content = bits;
    this.size = bits.reduce((acc, part) => {
      if (typeof part === 'string') return acc + part.length;
      if (part instanceof ArrayBuffer) return acc + part.byteLength;
      return acc;
    }, 0);
    this.type = options?.type || '';
  }

  arrayBuffer(): Promise<ArrayBuffer> {
    return Promise.resolve(new ArrayBuffer(this.size));
  }

  slice(start?: number, end?: number, contentType?: string): Blob {
    return new Blob(this._content.slice(start, end), { type: contentType || this.type });
  }

  stream(): ReadableStream {
    return new ReadableStream();
  }

  text(): Promise<string> {
    return Promise.resolve(this._content.map(part => 
      typeof part === 'string' ? part : 
      part instanceof ArrayBuffer ? new TextDecoder().decode(part) : ''
    ).join(''));
  }
} as any;
