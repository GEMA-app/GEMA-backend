class DomainException(Exception):
    """Clase base para todas las excepciones del dominio."""
    pass


class AuthException(DomainException):
    """Clase base para excepciones del módulo de autenticación."""
    pass


class WeakPasswordError(AuthException):
    """Lanzada cuando la contraseña en texto plano no cumple con las reglas de complejidad."""
    pass


class InvalidEmailError(AuthException):
    """Lanzada cuando la dirección de correo electrónico tiene un formato inválido."""
    pass


class UserAlreadyExistsError(AuthException):
    """Lanzada cuando se intenta registrar un usuario con un correo electrónico ya registrado."""
    pass


class InvalidCredentialsError(AuthException):
    """Lanzada cuando el correo o la contraseña son incorrectos durante el inicio de sesión."""
    pass


class UserInactiveError(AuthException):
    """Lanzada cuando se intenta realizar una acción con un usuario inactivo o suspendido."""
    pass


class InvalidTokenError(AuthException):
    """Lanzada cuando un token de autenticación es inválido, revocado o ha expirado."""
    pass


class CompanyException(DomainException):
    """Clase base para excepciones del módulo de empresas."""
    pass


class CompanyNotFoundError(CompanyException):
    """Lanzada cuando una empresa no es encontrada."""
    pass


class CompanySlugExistsError(CompanyException):
    """Lanzada cuando se intenta crear o actualizar una empresa con un slug que ya existe."""
    pass


class RoleException(DomainException):
    """Clase base para excepciones del módulo de roles."""
    pass


class RoleNotFoundError(RoleException):
    """Lanzada cuando un rol no es encontrado."""
    pass


class RoleNameExistsError(RoleException):
    """Lanzada cuando se intenta crear un rol con un nombre que ya existe en la empresa."""
    pass


class PermissionException(DomainException):
    """Clase base para excepciones de permisos."""
    pass


class InsufficientPermissionsError(PermissionException):
    """Lanzada cuando un usuario no tiene los permisos suficientes para realizar una acción."""
    pass


class AssetException(DomainException):
    """Clase base para excepciones del módulo de activos."""
    pass


class AssetNotFoundError(AssetException):
    """Lanzada cuando un activo no es encontrado."""
    pass


class AssetCodeExistsError(AssetException):
    """Lanzada cuando se intenta registrar un activo con un código que ya existe en la empresa."""
    pass


class AssetSerialExistsError(AssetException):
    """Lanzada cuando se intenta registrar un activo con un número de serie que ya existe en la empresa."""
    pass


class LocationException(DomainException):
    """Clase base para excepciones del módulo de ubicaciones."""
    pass


class LocationNotFoundError(LocationException):
    """Lanzada cuando una ubicación no es encontrada."""
    pass


class LocationCircularReferenceError(LocationException):
    """Lanzada cuando se detecta una referencia circular en la jerarquía de ubicaciones."""
    pass


class LocationInvalidTypeHierarchyError(LocationException):
    """Lanzada cuando se intenta establecer una relación de jerarquía inválida entre tipos de ubicación."""
    pass

