{ buildNimPackage }:
buildNimPackage {
  pname = "hello";
  version = "0.1.0";
  src = ./.;
  lockFile = ./lock.json;
}
