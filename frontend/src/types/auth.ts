export interface User {
  id: number;
  username: string;
}

export interface AuthSession {
  access_token: string;
  token_type: "bearer";
  user: User;
}

export interface AuthCredentials {
  username: string;
  password: string;
}
