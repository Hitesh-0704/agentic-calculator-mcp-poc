const examples = [
  "Add 25 and 17",
  "Multiply 12 by 8",
  "Subtract 45 from 100",
  "Divide 144 by 12",
];

export default function ExamplePrompts({ onSelect }) {
  return (
    <div className="examples">
      {examples.map((example) => (
        <button key={example} onClick={() => onSelect(example)}>
          {example}
        </button>
      ))}
    </div>
  );
}
