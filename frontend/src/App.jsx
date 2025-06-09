// src/App.jsx
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";


export default function App() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Привет, shadcn!</h1>
      <Button>Нажми меня</Button>
      <h1 className="text-2xl font-bold">Форма входа</h1>
      <Input placeholder="Логин" />
      <Input placeholder="Пароль" type="password" />
      <Button>Войти</Button>
    </main>
  );
}
