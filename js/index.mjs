import WalletConnect from "@walletconnect/client";
import QRCodeModal from "@walletconnect/qrcode-modal";

console.log(WalletConnect.default)
console.log(QRCodeModal)

async function happyPath() {
  // Create a connector
  const connector = new WalletConnect.default({
    bridge: "https://uniswap.bridge.walletconnect.org", // Required
    qrcodeModal: QRCodeModal
  });

  connector.on("session_update", (error, payload) => {
    if (error) {
      throw error;
    }

    // Get updated accounts and chainId
    const { accounts, chainId } = payload.params[0];
    console.log(accounts, chainId)
  });

  connector.on("disconnect", (error, payload) => {
    if (error) {
      throw error;
    }

    // Delete connector
  });

  debugger;
  const { accounts, chainId } = await connector.connect();
  console.log(accounts, chainId)
}


happyPath()
