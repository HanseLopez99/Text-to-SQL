#!/bin/bash
# ============================================
# setup_mysql.sh
# Verifica o instala MySQL 8.4.10
# ============================================

echo "=== Verificación de MySQL 8.4.10 ==="

# Verificar si MySQL está instalado
if command -v mysql &> /dev/null; then
    VERSION=$(mysql --version 2>/dev/null)
    echo "MySQL encontrado: $VERSION"
    
    # Verificar versión
    if echo "$VERSION" | grep -q "8.4.10"; then
        echo "✓ MySQL 8.4.10 instalado correctamente"
    else
        echo "⚠ Versión diferente a 8.4.10 detectada"
        echo "  Se recomienda instalar la versión exacta 8.4.10"
    fi
else
    echo "✗ MySQL no encontrado"
    echo ""
    echo "Opciones de instalación:"
    echo ""
    echo "1. Docker (recomendado):"
    echo "   docker pull mysql:8.4.10"
    echo "   docker run -d --name mysql-text2sql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password mysql:8.4.10"
    echo ""
    echo "2. Binario directo (Linux):"
    echo "   wget https://downloads.mysql.com/archives/get/p/23/file/mysql-8.4.10-linux-glibc2.17-x86_64-minimal.tar.xz"
    echo ""
    echo "3. macOS (Homebrew):"
    echo "   brew install mysql@8.4"
    echo ""
    echo "4. Descargar desde:"
    echo "   https://dev.mysql.com/downloads/mysql/8.4.html"
fi

echo ""
echo "=== Crear base de datos para evaluación ==="

# Intentar crear la base de datos
mysql -u root -e "CREATE DATABASE IF NOT EXISTS text_to_sql_eval CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Base de datos 'text_to_sql_eval' creada"
else
    echo "⚠ No se pudo conectar a MySQL. Verifica que esté corriendo."
fi

echo ""
echo "=== Verificar configuración ONLY_FULL_GROUP_BY ==="
mysql -u root -e "SELECT @@sql_mode;" 2>/dev/null | grep -q "ONLY_FULL_GROUP_BY"
if [ $? -eq 0 ]; then
    echo "✓ ONLY_FULL_GROUP_BY está habilitado"
else
    echo "⚠ ONLY_FULL_GROUP_BY no está habilitado (requerido por el proyecto)"
fi

echo ""
echo "=== Setup completado ==="
